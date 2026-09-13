"""
prometheus/api/routers/ml_anomaly.py
Phase 09 — ML Anomaly Detection endpoint.

GET /api/ml-anomaly   — run Isolation Forest on current DB flights
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml-anomaly", tags=["ML — Anomaly Detection"])


# ── Response schemas ──────────────────────────────────────────────────────────

class AnomalyFlight(BaseModel):
    airline:       str
    price:         float
    origin:        str
    destination:   str
    anomaly_score: float
    is_anomaly:    bool
    alert_level:   str     # NORMAL | WATCH | HIGH
    scraped_at:    str


class AnomalyResponse(BaseModel):
    origin:          str
    destination:     str
    total_flights:   int
    anomalies_found: int
    high_alerts:     int
    watch_alerts:    int
    flights:         list[AnomalyFlight]


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("", response_model=AnomalyResponse)
async def get_anomaly_scores(
    origin:      str = Query(default="DEL", description="IATA origin code"),
    destination: str = Query(default="BOM", description="IATA destination code"),
    limit:       int = Query(default=100, ge=1, le=500),
) -> AnomalyResponse:
    """
    Run Isolation Forest anomaly detection on the most recent flights
    from PostgreSQL and return per-flight anomaly scores.

    Returns 404 if no flight data exists (run POST /api/scrape first).
    """
    from sqlalchemy import text
    from prometheus.database.session import get_db_session
    from prometheus.ml.anomaly import score_flights

    origin = origin.upper()
    destination = destination.upper()

    # Load flights from DB
    flights_raw: list[dict[str, Any]] = []
    try:
        async with get_db_session() as session:
            result = await session.execute(
                text("""
                    SELECT airline, price, origin, destination,
                           departure_time, arrival_time, duration,
                           stops, currency, source_platform, scraped_at
                    FROM flights
                    WHERE origin = :origin AND destination = :destination
                    ORDER BY scraped_at DESC
                    LIMIT :lim
                """),
                {"origin": origin, "destination": destination, "lim": limit},
            )
            flights_raw = [dict(r) for r in result.mappings().all()]
    except Exception as exc:
        logger.error("DB query failed in ml-anomaly: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable")

    if not flights_raw:
        raise HTTPException(
            status_code=404,
            detail="No flight data available. Run POST /api/scrape first.",
        )

    # Score with Isolation Forest
    try:
        scored = score_flights(flights_raw)
    except Exception as exc:
        logger.error("Anomaly scoring failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {exc}")

    anomaly_flights = [
        AnomalyFlight(
            airline=f.get("airline", ""),
            price=float(f.get("price", 0)),
            origin=f.get("origin", ""),
            destination=f.get("destination", ""),
            anomaly_score=f.get("anomaly_score", 0.0),
            is_anomaly=f.get("is_anomaly", False),
            alert_level=f.get("alert_level", "NORMAL"),
            scraped_at=str(f.get("scraped_at", "")),
        )
        for f in scored
    ]

    high_count  = sum(1 for f in anomaly_flights if f.alert_level == "HIGH")
    watch_count = sum(1 for f in anomaly_flights if f.alert_level == "WATCH")

    return AnomalyResponse(
        origin=origin,
        destination=destination,
        total_flights=len(anomaly_flights),
        anomalies_found=sum(1 for f in anomaly_flights if f.is_anomaly),
        high_alerts=high_count,
        watch_alerts=watch_count,
        flights=anomaly_flights,
    )
