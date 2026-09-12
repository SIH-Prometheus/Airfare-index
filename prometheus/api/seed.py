"""
seed.py — In-memory mock data for Phase 7.
Replace with real asyncpg queries in Phase 8 once DB is populated.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from typing import Any

# ── Reference data ──────────────────────────────────────────────────────────────

AIRLINES: list[dict[str, Any]] = [
    {"id": 1, "code": "6E", "name": "IndiGo",    "iata_code": "IGO"},
    {"id": 2, "code": "AI", "name": "Air India",  "iata_code": "AIC"},
    {"id": 3, "code": "QP", "name": "Akasa Air",  "iata_code": "AKJ"},
]

AIRPORTS: list[dict[str, Any]] = [
    {"id": 1, "code": "DEL", "city": "Delhi",     "country": "India"},
    {"id": 2, "code": "BOM", "city": "Mumbai",    "country": "India"},
    {"id": 3, "code": "BLR", "city": "Bengaluru", "country": "India"},
    {"id": 4, "code": "MAA", "city": "Chennai",   "country": "India"},
    {"id": 5, "code": "HYD", "city": "Hyderabad", "country": "India"},
    {"id": 6, "code": "CCU", "city": "Kolkata",   "country": "India"},
]

ROUTES: list[dict[str, Any]] = [
    {"id": 1, "origin": "DEL", "destination": "BOM", "distance_km": 1148, "weight": 0.25},
    {"id": 2, "origin": "DEL", "destination": "BLR", "distance_km": 1742, "weight": 0.20},
    {"id": 3, "origin": "BOM", "destination": "BLR", "distance_km": 845,  "weight": 0.20},
    {"id": 4, "origin": "DEL", "destination": "MAA", "distance_km": 1754, "weight": 0.15},
    {"id": 5, "origin": "HYD", "destination": "DEL", "distance_km": 1253, "weight": 0.20},
]

# ── Helper ───────────────────────────────────────────────────────────────────────

def _daterange(days: int = 90) -> list[date]:
    today = date.today()
    return [today - timedelta(days=d) for d in range(days - 1, -1, -1)]


def _seed_index_history(days: int = 90) -> list[dict[str, Any]]:
    """Generate 90 days of realistic APIx values starting at 100."""
    dates = _daterange(days)
    rng = random.Random(42)
    value = 100.0
    history: list[dict[str, Any]] = []
    for i, d in enumerate(dates):
        change = rng.gauss(0.08, 0.6)          # slight upward drift
        value = round(max(95.0, value + change), 2)
        history.append({
            "id": i + 1,
            "date": d,
            "index_value": value,
            "index_type": "APIx",
            "route_id": None,
        })
    return history


def _seed_route_index(days: int = 90) -> list[dict[str, Any]]:
    """Route-level index history for each of the 5 routes."""
    dates = _daterange(days)
    rng = random.Random(7)
    records: list[dict[str, Any]] = []
    _id = 1
    for route in ROUTES:
        value = 100.0 + rng.uniform(-5, 5)
        for d in dates:
            change = rng.gauss(0.1, 0.8)
            value = round(max(90.0, value + change), 2)
            records.append({
                "id": _id,
                "date": d,
                "index_value": value,
                "index_type": "RouteIndex",
                "route_id": route["id"],
            })
            _id += 1
    return records


def _seed_fares(n: int = 300) -> list[dict[str, Any]]:
    rng = random.Random(13)
    today = date.today()
    fares: list[dict[str, Any]] = []
    for i in range(n):
        route    = rng.choice(ROUTES)
        airline  = rng.choice(AIRLINES)
        adv_days = rng.choice([1, 7, 15, 30])
        obs_date = today - timedelta(days=rng.randint(0, 89))
        dep_date = obs_date + timedelta(days=adv_days)
        base     = round(rng.uniform(2500, 9500), 2)
        taxes    = round(base * rng.uniform(0.08, 0.18), 2)
        fares.append({
            "id":               i + 1,
            "airline":          airline["name"],
            "airline_code":     airline["code"],
            "source":           "scraper",
            "origin":           route["origin"],
            "destination":      route["destination"],
            "route_id":         route["id"],
            "observation_date": obs_date,
            "departure_date":   dep_date,
            "advance_days":     adv_days,
            "base_fare":        base,
            "taxes":            taxes,
            "total_fare":       round(base + taxes, 2),
            "currency":         "INR",
            "scraped_at":       datetime.combine(obs_date, datetime.min.time()),
        })
    return fares


def _seed_alerts(index_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate one alert per week from index history."""
    rng = random.Random(99)
    severities = ["NORMAL", "WATCH", "ELEVATED", "HIGH"]
    weights    = [0.50, 0.25, 0.15, 0.10]
    alerts: list[dict[str, Any]] = []
    weeks = index_history[::7]           # every 7th entry
    for i, entry in enumerate(weeks):
        severity = rng.choices(severities, weights)[0]
        wow      = round(rng.uniform(-3.0, 8.0), 2)
        z_score  = round(rng.uniform(-1.5, 2.5), 2)
        score    = round(abs(wow) * 0.4 + abs(z_score) * 0.6, 2)
        alerts.append({
            "id":            i + 1,
            "severity":      severity,
            "score":         score,
            "wow_change":    wow,
            "z_score":       z_score,
            "anomaly_score": round(rng.uniform(0.0, 1.0), 3),
            "contributors":  [r["id"] for r in rng.choices(ROUTES, k=2)],
            "apix_value":    entry["index_value"],
            "created_at":    datetime.combine(entry["date"], datetime.min.time()),
        })
    return alerts


# ── Module-level seed ────────────────────────────────────────────────────────────

INDEX_HISTORY:  list[dict[str, Any]] = _seed_index_history(90)
ROUTE_INDEX:    list[dict[str, Any]] = _seed_route_index(90)
FARE_OBS:       list[dict[str, Any]] = _seed_fares(300)
ALERTS:         list[dict[str, Any]] = _seed_alerts(INDEX_HISTORY)
