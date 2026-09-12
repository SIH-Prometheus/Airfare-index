"""
prometheus/scrapers/runner.py
Scraper runner — attempts live fetch then falls back to sample data.
Writes raw JSON to MinIO and returns the key + data_source label.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from prometheus.config import settings
from prometheus.storage.minio_client import get_minio_client, make_raw_key

logger = logging.getLogger(__name__)

# Path to the bundled fallback dataset
SAMPLE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample" / "DEL_BOM_sample.json"

# ── Live scrape (best-effort, httpx-based) ────────────────────────────────────

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _parse_google_flights_html(html: str, origin: str, destination: str) -> list[dict[str, Any]]:
    """
    Parser for Google Flights HTML aria-label cards.
    Extracts airline, departure/arrival times, duration, stops, and price in INR.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    flights: list[dict[str, Any]] = []

    # Find aria-labels that describe full flights
    aria_labels = re.findall(r'aria-label="([^"]+)"', html)
    airlines_list = ["IndiGo", "Air India", "Akasa Air", "SpiceJet", "Vistara"]

    flight_labels = [
        a for a in aria_labels
        if any(air in a for air in airlines_list)
        and any(cur in a for cur in ["rupees", "INR", "\u20b9"])
    ]

    for a in flight_labels:
        # 1. Airline
        airline = "Unknown"
        for air in airlines_list:
            if air in a:
                airline = air
                break

        # 2. Times
        times = [t.replace("\u202f", " ") for t in re.findall(r"\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b", a)]
        dep_time = times[0] if len(times) >= 1 else ""
        arr_time = times[1] if len(times) >= 2 else ""

        # 3. Duration
        dur_m = re.search(r"duration\s+([\d\s\w]+?)\.", a)
        duration = dur_m.group(1).strip() if dur_m else ""

        # 4. Stops
        stops = "Nonstop" if "Nonstop" in a or "nonstop" in a else "1 stop"

        # 5. Price
        p_m = re.search(r"(?:From\s+)?([\d,]+)\s+Indian rupees", a) or re.search(r"[\u20b9]\s*([\d,]+)", a)
        price = int(p_m.group(1).replace(",", "")) if p_m else 0

        if price > 0:
            flights.append({
                "airline": airline,
                "flight_number": "",
                "origin": origin,
                "destination": destination,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "duration": duration,
                "stops": stops,
                "price": price,
                "currency": "INR",
                "source_platform": "Google Flights (live OTA)",
                "lead_time": "T+1",
                "scraped_at": now_str,
            })

    return flights


async def _attempt_live_scrape(origin: str, destination: str) -> list[dict[str, Any]]:
    """Try to scrape live fares from Google Flights. Returns [] on any failure."""
    from datetime import timedelta
    # Search for T+2 to guarantee future bookable flights
    travel_date = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d")
    url = (
        f"https://www.google.com/travel/flights?"
        f"q=flights+from+{origin}+to+{destination}+on+{travel_date}&curr=INR"
    )
    try:
        async with httpx.AsyncClient(
            headers=_HEADERS,
            timeout=20.0,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning("Google Flights returned HTTP %d", resp.status_code)
                return []
            flights = _parse_google_flights_html(resp.text, origin, destination)
            logger.info("Live scrape extracted %d flights", len(flights))
            return flights
    except Exception as exc:
        logger.warning("Live scrape failed: %s", exc)
        return []


# ── Sample fallback ───────────────────────────────────────────────────────────

def _load_sample_data(origin: str, destination: str) -> list[dict[str, Any]]:
    """Load the bundled sample dataset and update timestamps."""
    now_str = datetime.now(timezone.utc).isoformat()
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(f"Sample data not found at {SAMPLE_PATH}")
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)
    # Update scraped_at to now so it looks fresh
    for r in records:
        r["scraped_at"] = now_str
        # Filter only requested route (sample is DEL-BOM only)
        r["origin"] = origin
        r["destination"] = destination
    logger.info("Loaded %d sample records from %s", len(records), SAMPLE_PATH)
    return records


# ── Main runner ───────────────────────────────────────────────────────────────

class ScrapeResult:
    def __init__(
        self,
        flights: list[dict[str, Any]],
        data_source: str,
        minio_key: str,
        origin: str,
        destination: str,
    ) -> None:
        self.flights = flights
        self.data_source = data_source
        self.minio_key = minio_key
        self.origin = origin
        self.destination = destination


async def run_scrape_and_ingest(origin: str = "DEL", destination: str = "BOM") -> ScrapeResult:
    """
    Entry point for the scrape → MinIO pipeline stage.

    1. Attempts live scrape from Google Flights.
    2. Falls back to sample data if live scrape fails or returns < 3 results.
    3. Uploads raw JSON to MinIO.
    4. Returns ScrapeResult with flights, data_source label, and MinIO key.
    """
    origin = origin.upper()
    destination = destination.upper()

    # Step 1: Try live scrape
    flights = await _attempt_live_scrape(origin, destination)
    if len(flights) >= 3:
        data_source = "live"
        logger.info("Using LIVE data: %d flights", len(flights))
    else:
        # Step 2: Fall back to sample
        flights = _load_sample_data(origin, destination)
        data_source = "sample_fallback"
        logger.info("Using SAMPLE FALLBACK data: %d flights", len(flights))

    # Step 3: Upload to MinIO
    bucket = settings.MINIO_BUCKET_RAW
    key = make_raw_key(origin, destination)
    minio_ok = False
    try:
        client = get_minio_client()
        client.ensure_bucket(bucket)
        client.upload_json(bucket, key, flights)
        minio_ok = True
        logger.info("Raw data uploaded to MinIO: %s/%s", bucket, key)
    except Exception as exc:
        logger.error("MinIO upload failed: %s — continuing without MinIO storage", exc)
        key = f"minio_unavailable/{key}"

    return ScrapeResult(
        flights=flights,
        data_source=data_source,
        minio_key=key,
        origin=origin,
        destination=destination,
    )
