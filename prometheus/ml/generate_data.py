import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# -----------------------------
# Configuration
# -----------------------------

NUM_DAYS = 365

routes = {
    "DEL-BOM": 6200,
    "DEL-BLR": 6800,
    "BOM-BLR": 5000,
    "DEL-CCU": 6500,
    "DEL-HYD": 6100,
    "BOM-MAA": 5900,
    "BLR-HYD": 4200,
    "DEL-MAA": 7200,
    "BOM-GOI": 5200,
    "DEL-SXR": 7800,
}

airlines = [
    ("IndiGo", "6E"),
    ("Air India", "AI"),
    ("Air India Express", "IX"),
    ("Akasa Air", "QP"),
]

sources = [
    "EaseMyTrip",
    "MakeMyTrip",
    "Cleartrip",
]

lead_times = [1, 2, 3, 5, 7, 10, 14, 21, 30]

# Start date
start_date = datetime(2025, 10, 1)

# -----------------------------
# Festival / seasonal effects
# -----------------------------

def seasonal_factor(date, route):
    factor = 1.0

    # Diwali / festive season
    if (date.month == 10 and date.day >= 18) or (
        date.month == 11 and date.day <= 5
    ):
        factor *= 1.28

        if route in ["DEL-SXR", "BOM-GOI"]:
            factor *= 1.12

    # Christmas + New Year
    if (date.month == 12 and date.day >= 18) or (
        date.month == 1 and date.day <= 5
    ):
        factor *= 1.22

    # Holi / spring travel
    if date.month == 3 and 10 <= date.day <= 31:
        factor *= 1.15

    # Independence Day travel
    if date.month == 8 and 10 <= date.day <= 20:
        factor *= 1.12

    # Summer vacation
    if date.month in [5, 6]:
        factor *= 1.12

        if route in ["BOM-GOI", "DEL-SXR"]:
            factor *= 1.10

    return factor


# -----------------------------
# Short abnormal price shocks
# -----------------------------

shocks = {
    datetime(2025, 11, 7).date(): 1.40,
    datetime(2026, 1, 14).date(): 1.30,
    datetime(2026, 4, 18).date(): 1.42,
    datetime(2026, 7, 9).date(): 1.34,
    datetime(2026, 8, 15).date(): 1.46,
}


def shock_factor(date):
    """
    Each shock lasts approximately 3 days.
    """

    for shock_date, multiplier in shocks.items():

        difference = (date.date() - shock_date).days

        if 0 <= difference <= 2:
            return multiplier

    return 1.0


# -----------------------------
# Generate records
# -----------------------------

records = []

record_id = 1

for day_number in range(NUM_DAYS):

    date = start_date + timedelta(days=day_number)

    for route, base_price in routes.items():

        origin, destination = route.split("-")

        # Gradual fuel / macro trend
        fuel_factor = (
            1.0
            + 0.00045 * day_number
            + 0.022 * math.sin(2 * math.pi * day_number / 90)
        )

        macro_factor = (
            1.0
            + 0.015 * math.sin(2 * math.pi * day_number / 180)
        )

        # Weekly demand pattern
        weekly_factor = 1.0

        if date.weekday() in [4, 6]:       # Friday / Sunday
            weekly_factor *= 1.045

        elif date.weekday() == 1:          # Tuesday
            weekly_factor *= 0.985

        # Festival / seasonal effect
        season_factor = seasonal_factor(date, route)

        # Temporary anomaly
        abnormal_factor = shock_factor(date)

        # Route sensitivity
        route_sensitivity = 1.20 if route in [
            "DEL-SXR",
            "BOM-GOI"
        ] else 0.90

        # Choose booking horizon
        lead_days = random.choice(lead_times)

        # Near-departure pricing effect
        booking_factor = (
            1 + 0.38 * math.exp(-lead_days / 8)
        )

        # Random noise
        noise = random.gauss(0, 0.035)

        # Final price
        price = (
            base_price
            * fuel_factor
            * macro_factor
            * weekly_factor
            * season_factor
            * (
                1
                + route_sensitivity
                * (booking_factor - 1)
            )
            * abnormal_factor
            * (1 + noise)
        )

        price = max(1800, round(price))

        # Airline
        airline, code = random.choice(airlines)

        flight_number = (
            f"{code}-{random.randint(100, 9999)}"
        )

        # Flight timing
        departure_hour = random.choice([
            5, 6, 7, 8, 9, 10,
            12, 14, 16, 18, 20, 22
        ])

        departure_minute = random.choice([
            0, 5, 10, 15, 20, 25,
            30, 35, 40, 45, 50, 55
        ])

        departure_time = (
            f"{departure_hour:02d}:{departure_minute:02d}"
        )

        duration_minutes = random.randint(
            100, 190
        )

        arrival_minutes = (
            departure_hour * 60
            + departure_minute
            + duration_minutes
        )

        arrival_hour = (arrival_minutes // 60) % 24
        arrival_minute = arrival_minutes % 60

        arrival_time = (
            f"{arrival_hour:02d}:{arrival_minute:02d}"
        )

        duration_hours = duration_minutes // 60
        duration_remaining = duration_minutes % 60

        duration = (
            f"{duration_hours:02d}h "
            f"{duration_remaining:02d}m"
        )

        record = {
            "airline": airline,
            "flight_number": flight_number + "ECONOMY",
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "origin": origin,
            "destination": destination,
            "duration": duration,
            "stops": "Non-stop",
            "price": price,
            "currency": "INR",
            "source_platform": random.choice(sources),
            "lead_time": f"T+{lead_days}",
            "scraped_at": (
                date.replace(
                    hour=11,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                    microsecond=0
                ).isoformat()
                + "+00:00"
            ),
        }

        records.append(record)

        record_id += 1


# -----------------------------
# Save
# -----------------------------

output_path = (
    Path(__file__).resolve().parent
    / "data"
    / "matrix_flights_3650.json"
)

with open(output_path, "w") as f:
    json.dump(records, f, indent=2)

print("=" * 60)
print("DATASET GENERATED")
print("=" * 60)
print(f"Records : {len(records)}")
print(f"Routes  : {len(routes)}")
print(f"Days    : {NUM_DAYS}")
print(f"Output  : {output_path}")
print("=" * 60)