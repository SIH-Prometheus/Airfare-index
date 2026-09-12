"""
prometheus/index/calculator.py
Simple deterministic airfare index calculator for the MVP.

Formula:
    Airfare Index = (Average Fare / Baseline Fare) × 100
    Baseline Fare = ₹4,500 (DEL → BOM)

No ML. No forecasting. Pure arithmetic.
Extension point: swap baseline or formula in Phase 2.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

# ── Baseline ──────────────────────────────────────────────────────────────────
BASELINE_FARE_INR: float = 4_500.0


# ── Output schema ────────────────────────────────────────────────────────────

@dataclass
class AirlineFare:
    airline: str
    average_fare: float
    min_fare: float
    max_fare: float
    count: int


@dataclass
class IndexResult:
    average_fare: float
    minimum_fare: float
    maximum_fare: float
    airfare_index: float
    airline_fares: list[AirlineFare] = field(default_factory=list)
    baseline_fare: float = BASELINE_FARE_INR
    sample_size: int = 0


# ── Calculator ────────────────────────────────────────────────────────────────

def calculate_index(flights: list[dict[str, Any]]) -> IndexResult | None:
    """
    Calculate the Airfare Price Index from a list of cleaned flight dicts.

    Returns None if the flight list is empty or has no valid prices.

    Extension point for Phase 2:
    - Replace simple avg formula with Jevons / Laspeyres / Paasche index
    - Add route weighting
    - Connect to ML anomaly detection
    """
    prices: list[float] = []
    airline_buckets: dict[str, list[float]] = defaultdict(list)

    for f in flights:
        price = f.get("price")
        if not isinstance(price, (int, float)) or price <= 0:
            continue
        price = float(price)
        prices.append(price)
        airline = f.get("airline", "Unknown")
        airline_buckets[airline].append(price)

    if not prices:
        return None

    avg = sum(prices) / len(prices)
    minimum = min(prices)
    maximum = max(prices)
    index_value = round((avg / BASELINE_FARE_INR) * 100, 2)

    airline_fares: list[AirlineFare] = []
    for airline, fare_list in sorted(airline_buckets.items()):
        airline_fares.append(AirlineFare(
            airline=airline,
            average_fare=round(sum(fare_list) / len(fare_list), 2),
            min_fare=round(min(fare_list), 2),
            max_fare=round(max(fare_list), 2),
            count=len(fare_list),
        ))

    return IndexResult(
        average_fare=round(avg, 2),
        minimum_fare=round(minimum, 2),
        maximum_fare=round(maximum, 2),
        airfare_index=index_value,
        airline_fares=airline_fares,
        baseline_fare=BASELINE_FARE_INR,
        sample_size=len(prices),
    )
