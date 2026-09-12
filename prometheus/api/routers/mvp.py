"""
prometheus/api/routers/mvp.py
MVP endpoints for the DEL→BOM Airfare Price Index dashboard.

Endpoints:
    POST /api/scrape            — trigger full pipeline (scraper→MinIO→ETL→PG→Index)
    GET  /api/airfare-index     — current index metrics
    GET  /api/airfare-index/trend — historical trend for chart
    GET  /api/flights           — flight records from DB
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from prometheus.database.session import get_db_session
from prometheus.etl.pipeline import run_etl
from prometheus.index.calculator import calculate_index
from prometheus.scrapers.runner import run_scrape_and_ingest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["MVP — DEL→BOM"])


# ── Pydantic response schemas ─────────────────────────────────────────────────

class AirlineFareSchema(BaseModel):
    airline: str
    average_fare: float


class PipelineStatusSchema(BaseModel):
    """Mutable during request processing — model_config allows attribute assignment."""
    model_config = ConfigDict(frozen=False)

    scraper:    str = "pending"
    minio:      str = "pending"
    postgresql: str = "pending"
    index:      str = "pending"


class ScrapeMetrics(BaseModel):
    average_fare:  float
    minimum_fare:  float
    maximum_fare:  float
    airfare_index: float
    baseline_fare: float
    sample_size:   int
    etl_inserted:  int


class ScrapeResponse(BaseModel):
    success:       bool
    origin:        str
    destination:   str
    data_source:   str
    pipeline:      PipelineStatusSchema
    metrics:       ScrapeMetrics
    airline_fares: list[AirlineFareSchema]
    scraped_at:    str


class AirfareIndexResponse(BaseModel):
    success:       bool
    origin:        str
    destination:   str
    data_source:   str
    metrics:       ScrapeMetrics
    airline_fares: list[AirlineFareSchema]
    calculated_at: str


class TrendPoint(BaseModel):
    calculated_at: str
    average_fare:  float
    minimum_fare:  float
    maximum_fare:  float
    airfare_index: float


class FlightRecord(BaseModel):
    id:              int
    airline:         str
    flight_number:   str
    origin:          str
    destination:     str
    departure_time:  str
    arrival_time:    str
    duration:        str
    stops:           str
    price:           float
    currency:        str
    source_platform: str
    scraped_at:      str


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _load_flights_from_db(
    origin: str, destination: str
) -> list[dict[str, Any]]:
    """Fetch the most recent flights for a route from PostgreSQL."""
    from sqlalchemy import text
    async with get_db_session() as session:
        result = await session.execute(
            text("""
                SELECT airline, flight_number, origin, destination,
                       departure_time, arrival_time, duration, stops,
                       price, currency, source_platform, lead_time, scraped_at
                FROM flights
                WHERE origin = :origin AND destination = :destination
                ORDER BY scraped_at DESC
                LIMIT 200
            """),
            {"origin": origin, "destination": destination},
        )
        return [dict(r) for r in result.mappings().all()]


async def _get_airline_fares_from_db(
    origin: str, destination: str
) -> list[AirlineFareSchema]:
    """Airline-wise average fares from flights table."""
    from sqlalchemy import text
    try:
        async with get_db_session() as session:
            result = await session.execute(
                text("""
                    SELECT airline, AVG(price) AS avg_fare
                    FROM flights
                    WHERE origin = :origin AND destination = :destination
                    GROUP BY airline
                    ORDER BY airline
                """),
                {"origin": origin, "destination": destination},
            )
            return [
                AirlineFareSchema(
                    airline=r["airline"],
                    average_fare=round(float(r["avg_fare"]), 2),
                )
                for r in result.mappings().all()
            ]
    except Exception as exc:
        logger.warning("Airline fares DB query failed: %s", exc)
        return []


async def _save_index_snapshot(
    origin: str,
    destination: str,
    avg: float,
    minimum: float,
    maximum: float,
    apix: float,
    data_source: str,
) -> None:
    """Persist an index calculation result to the airfare_index table."""
    from sqlalchemy import text
    try:
        async with get_db_session() as session:
            await session.execute(
                text("""
                    INSERT INTO airfare_index
                        (origin, destination, travel_date,
                         average_fare, minimum_fare, maximum_fare,
                         airfare_index, data_source, calculated_at)
                    VALUES
                        (:origin, :destination, CURRENT_DATE,
                         :avg_fare, :min_fare, :max_fare,
                         :apix_val, :dsource, NOW())
                """),
                {
                    "origin":    origin,
                    "destination": destination,
                    "avg_fare":  avg,
                    "min_fare":  minimum,
                    "max_fare":  maximum,
                    "apix_val":  apix,
                    "dsource":   data_source,
                },
            )
    except Exception as exc:
        logger.error("Failed to save index snapshot: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/scrape
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    origin:      str = Query(default="DEL", description="IATA origin code"),
    destination: str = Query(default="BOM", description="IATA destination code"),
) -> ScrapeResponse:
    """
    Run the full DEL→BOM pipeline:
      1. Scrape Google Flights (httpx, best-effort)
      2. Fall back to sample data if scrape fails
      3. Upload raw JSON to MinIO
      4. ETL → PostgreSQL
      5. Calculate Airfare Index
    """
    origin      = origin.upper()
    destination = destination.upper()
    now_str     = datetime.now(timezone.utc).isoformat()

    ps = PipelineStatusSchema()   # mutable Pydantic model

    # ── Stage 1: Scraper + MinIO ─────────────────────────────────────────────
    try:
        scrape_result = await run_scrape_and_ingest(origin, destination)
        ps.scraper = "ok"
        ps.minio   = "error" if "minio_unavailable" in scrape_result.minio_key else "ok"
        flights_raw  = scrape_result.flights
        data_source  = scrape_result.data_source
    except Exception as exc:
        logger.error("Scrape stage failed: %s", exc)
        ps.scraper = "error"
        ps.minio   = "error"
        raise HTTPException(status_code=503, detail=f"Scraper failed: {exc}")

    # ── Stage 2: ETL → PostgreSQL ────────────────────────────────────────────
    etl_inserted = 0
    try:
        async with get_db_session() as session:
            etl_stats    = await run_etl(flights_raw, session)
            etl_inserted = etl_stats.get("inserted", 0)
        ps.postgresql = "ok"
    except Exception as exc:
        logger.error("ETL/PostgreSQL stage failed: %s", exc)
        ps.postgresql = "error"

    # ── Stage 3: Load cleaned flights (DB preferred, raw as fallback) ────────
    try:
        flights_for_index = await _load_flights_from_db(origin, destination)
        if not flights_for_index:
            flights_for_index = flights_raw
    except Exception:
        flights_for_index = flights_raw

    # ── Stage 4: Calculate index ─────────────────────────────────────────────
    index_result = calculate_index(flights_for_index)
    if index_result is None:
        ps.index = "error"
        raise HTTPException(status_code=500, detail="No valid prices to compute index")
    ps.index = "ok"

    # ── Stage 5: Persist index snapshot ─────────────────────────────────────
    if ps.postgresql == "ok":
        await _save_index_snapshot(
            origin, destination,
            index_result.average_fare,
            index_result.minimum_fare,
            index_result.maximum_fare,
            index_result.airfare_index,
            data_source,
        )

    return ScrapeResponse(
        success=True,
        origin=origin,
        destination=destination,
        data_source=data_source,
        pipeline=ps,
        metrics=ScrapeMetrics(
            average_fare=index_result.average_fare,
            minimum_fare=index_result.minimum_fare,
            maximum_fare=index_result.maximum_fare,
            airfare_index=index_result.airfare_index,
            baseline_fare=index_result.baseline_fare,
            sample_size=index_result.sample_size,
            etl_inserted=etl_inserted,
        ),
        airline_fares=[
            AirlineFareSchema(airline=af.airline, average_fare=af.average_fare)
            for af in index_result.airline_fares
        ],
        scraped_at=now_str,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/airfare-index
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/airfare-index", response_model=AirfareIndexResponse)
async def get_airfare_index(
    origin:      str = Query(default="DEL"),
    destination: str = Query(default="BOM"),
) -> AirfareIndexResponse:
    """
    Return the most recent airfare index snapshot from PostgreSQL.
    Falls back to on-the-fly calculation from flights table.
    Returns 404 if no data exists yet (run POST /api/scrape first).
    """
    from sqlalchemy import text

    origin      = origin.upper()
    destination = destination.upper()

    # Try snapshot table first
    snapshot = None
    try:
        async with get_db_session() as session:
            row = await session.execute(
                text("""
                    SELECT average_fare, minimum_fare, maximum_fare,
                           airfare_index, data_source, calculated_at
                    FROM airfare_index
                    WHERE origin = :origin AND destination = :destination
                    ORDER BY calculated_at DESC
                    LIMIT 1
                """),
                {"origin": origin, "destination": destination},
            )
            snapshot = row.mappings().first()
    except Exception as exc:
        logger.warning("Snapshot query failed: %s", exc)

    if snapshot:
        airline_fares = await _get_airline_fares_from_db(origin, destination)
        return AirfareIndexResponse(
            success=True,
            origin=origin,
            destination=destination,
            data_source=str(snapshot["data_source"]),
            metrics=ScrapeMetrics(
                average_fare=float(snapshot["average_fare"]),
                minimum_fare=float(snapshot["minimum_fare"]),
                maximum_fare=float(snapshot["maximum_fare"]),
                airfare_index=float(snapshot["airfare_index"]),
                baseline_fare=4500.0,
                sample_size=0,
                etl_inserted=0,
            ),
            airline_fares=airline_fares,
            calculated_at=str(snapshot["calculated_at"]),
        )

    # Fallback: compute from flights table
    try:
        flights = await _load_flights_from_db(origin, destination)
    except Exception:
        flights = []

    if not flights:
        raise HTTPException(
            status_code=404,
            detail="No data available. Run POST /api/scrape?origin=DEL&destination=BOM first.",
        )

    result = calculate_index(flights)
    if result is None:
        raise HTTPException(status_code=500, detail="Cannot compute index — no valid prices")

    return AirfareIndexResponse(
        success=True,
        origin=origin,
        destination=destination,
        data_source="database_computed",
        metrics=ScrapeMetrics(
            average_fare=result.average_fare,
            minimum_fare=result.minimum_fare,
            maximum_fare=result.maximum_fare,
            airfare_index=result.airfare_index,
            baseline_fare=result.baseline_fare,
            sample_size=result.sample_size,
            etl_inserted=0,
        ),
        airline_fares=[
            AirlineFareSchema(airline=af.airline, average_fare=af.average_fare)
            for af in result.airline_fares
        ],
        calculated_at=datetime.now(timezone.utc).isoformat(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/airfare-index/trend
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/airfare-index/trend", response_model=list[TrendPoint])
async def get_trend(
    origin:      str = Query(default="DEL"),
    destination: str = Query(default="BOM"),
) -> list[TrendPoint]:
    """
    Return historical index snapshots for the trend chart.
    Only real observations are returned — no fabricated history.
    """
    from sqlalchemy import text

    origin      = origin.upper()
    destination = destination.upper()

    try:
        async with get_db_session() as session:
            result = await session.execute(
                text("""
                    SELECT calculated_at, average_fare, minimum_fare,
                           maximum_fare, airfare_index
                    FROM airfare_index
                    WHERE origin = :origin AND destination = :destination
                    ORDER BY calculated_at ASC
                    LIMIT 90
                """),
                {"origin": origin, "destination": destination},
            )
            rows = result.mappings().all()
    except Exception as exc:
        logger.error("Trend query failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable")

    return [
        TrendPoint(
            calculated_at=str(r["calculated_at"]),
            average_fare=float(r["average_fare"]),
            minimum_fare=float(r["minimum_fare"]),
            maximum_fare=float(r["maximum_fare"]),
            airfare_index=float(r["airfare_index"]),
        )
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/flights
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/flights", response_model=list[FlightRecord])
async def get_flights(
    origin:      str = Query(default="DEL"),
    destination: str = Query(default="BOM"),
    limit:       int = Query(default=50, ge=1, le=200),
) -> list[FlightRecord]:
    """List flight records from PostgreSQL for a given route."""
    from sqlalchemy import text

    origin      = origin.upper()
    destination = destination.upper()

    try:
        async with get_db_session() as session:
            result = await session.execute(
                text("""
                    SELECT id, airline, flight_number, origin, destination,
                           departure_time, arrival_time, duration, stops,
                           price, currency, source_platform, scraped_at
                    FROM flights
                    WHERE origin = :origin AND destination = :destination
                    ORDER BY scraped_at DESC
                    LIMIT :lim
                """),
                {"origin": origin, "destination": destination, "lim": limit},
            )
            rows = result.mappings().all()
    except Exception as exc:
        logger.error("Flights query failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable")

    return [
        FlightRecord(
            id=r["id"],
            airline=r["airline"],
            flight_number=r["flight_number"] or "",
            origin=r["origin"],
            destination=r["destination"],
            departure_time=str(r["departure_time"] or ""),
            arrival_time=str(r["arrival_time"] or ""),
            duration=r["duration"] or "",
            stops=r["stops"] or "",
            price=float(r["price"]),
            currency=r["currency"],
            source_platform=r["source_platform"] or "",
            scraped_at=str(r["scraped_at"]),
        )
        for r in rows
    ]
