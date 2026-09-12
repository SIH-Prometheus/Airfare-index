"""
prometheus/etl/pipeline.py
ETL pipeline: reads raw JSON from MinIO → validates → normalises → deduplicates → inserts into PostgreSQL.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# ── Airline name normalisation map ────────────────────────────────────────────
AIRLINE_ALIASES: dict[str, str] = {
    "indigo": "IndiGo",
    "6e": "IndiGo",
    "air india": "Air India",
    "airindia": "Air India",
    "ai": "Air India",
    "akasa air": "Akasa Air",
    "akasa": "Akasa Air",
    "qp": "Akasa Air",
    "spicejet": "SpiceJet",
    "spice jet": "SpiceJet",
    "sg": "SpiceJet",
    "vistara": "Vistara",
    "uk": "Vistara",
    "gofirst": "GoFirst",
    "go first": "GoFirst",
    "g8": "GoFirst",
    "goair": "GoAir",
}


def _normalise_airline(name: str) -> str:
    key = name.strip().lower()
    return AIRLINE_ALIASES.get(key, name.strip().title())


def _parse_price(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    # Strip non-numeric except dot
    cleaned = re.sub(r"[^\d.]", "", str(raw))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _record_hash(record: dict[str, Any]) -> str:
    """Deterministic dedup hash based on key fields."""
    key = "|".join(str(record.get(f, "")) for f in [
        "airline", "flight_number", "origin", "destination",
        "departure_time", "price",
    ])
    return hashlib.sha256(key.encode()).hexdigest()


# ── Validation ────────────────────────────────────────────────────────────────

def _validate(record: dict[str, Any]) -> bool:
    if not record.get("airline", "").strip():
        return False
    if not record.get("origin", "").strip():
        return False
    if not record.get("destination", "").strip():
        return False
    price = _parse_price(record.get("price"))
    if price is None or price <= 0:
        return False
    return True


# ── Normalise ─────────────────────────────────────────────────────────────────

def _normalise(record: dict[str, Any]) -> dict[str, Any]:
    price = _parse_price(record.get("price")) or 0.0
    scraped_at = record.get("scraped_at") or datetime.now(timezone.utc).isoformat()
    return {
        "airline": _normalise_airline(record.get("airline", "")),
        "flight_number": str(record.get("flight_number", "")).strip().upper(),
        "origin": str(record.get("origin", "")).strip().upper(),
        "destination": str(record.get("destination", "")).strip().upper(),
        "departure_time": str(record.get("departure_time", "")).strip(),
        "arrival_time": str(record.get("arrival_time", "")).strip(),
        "duration": str(record.get("duration", "")).strip(),
        "stops": str(record.get("stops", "non-stop")).strip().lower(),
        "price": price,
        "currency": str(record.get("currency", "INR")).strip().upper(),
        "source_platform": str(record.get("source_platform", "unknown")).strip(),
        "lead_time": str(record.get("lead_time", "")).strip(),
        "scraped_at": scraped_at,
    }


# ── Pipeline ─────────────────────────────────────────────────────────────────

async def run_etl(flights_raw: list[dict[str, Any]], session: AsyncSession) -> dict[str, int]:
    """
    Full ETL pipeline on a list of raw flight dicts.

    Returns a summary dict: {total, validated, inserted, duplicates_skipped, errors}.
    """
    stats = {
        "total": len(flights_raw),
        "validated": 0,
        "inserted": 0,
        "duplicates_skipped": 0,
        "errors": 0,
    }

    seen_hashes: set[str] = set()

    for raw in flights_raw:
        # Step 1: Validate
        if not _validate(raw):
            stats["errors"] += 1
            continue
        stats["validated"] += 1

        # Step 2: Normalise
        record = _normalise(raw)

        # Step 3: Deduplicate in-memory
        h = _record_hash(record)
        if h in seen_hashes:
            stats["duplicates_skipped"] += 1
            continue
        seen_hashes.add(h)

        # Step 4: Insert into PostgreSQL (upsert on hash)
        try:
            await session.execute(
                text("""
                    INSERT INTO flights (
                        airline, flight_number, origin, destination,
                        departure_time, arrival_time, duration, stops,
                        price, currency, source_platform, lead_time,
                        scraped_at, created_at, raw_hash
                    ) VALUES (
                        :airline, :flight_number, :origin, :destination,
                        :departure_time, :arrival_time, :duration, :stops,
                        :price, :currency, :source_platform, :lead_time,
                        :scraped_at, NOW(), :raw_hash
                    )
                    ON CONFLICT (raw_hash) DO NOTHING
                """),
                {**record, "raw_hash": h},
            )
            stats["inserted"] += 1
        except Exception as exc:
            logger.error("ETL insert error: %s | record: %s", exc, record)
            stats["errors"] += 1

    logger.info("ETL complete: %s", stats)
    return stats
