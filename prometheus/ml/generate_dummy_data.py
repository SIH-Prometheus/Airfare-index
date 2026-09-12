import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

OUTPUT = Path(__file__).resolve().parent / "matrix_flights_3000.json"

# ---------------------------------------------------------
# 10 important Indian domestic routes
# ---------------------------------------------------------

routes = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("DEL", "HYD"),
    ("BOM", "MAA"),
    ("BLR", "HYD"),
    ("DEL", "MAA"),
    ("BOM", "GOI"),
    ("DEL", "SXR"),
]

route_base_price = {
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

duration_range = {
    "DEL-BOM": (145, 175),
    "DEL-BLR": (160, 190),
    "BOM-BLR": (90, 125),
    "DEL-CCU": (130, 160),
    "DEL-HYD": (125, 155),
    "BOM-MAA": (110, 145),
    "BLR-HYD": (65, 95),
    "DEL-MAA": (160, 190),
    "BOM-GOI": (60, 90),
    "DEL-SXR": (90, 125),
}

airlines = {
    "IndiGo": "6E",
    "Air India": "AI",
    "Air India Express": "IX",
    "Akasa Air": "QP",
}

source_platforms = [
    "EaseMyTrip",
    "MakeMyTrip",
    "Cleartrip",
]

# ---------------------------------------------------------
# Recurring seasonal/festival behaviour
# ---------------------------------------------------------

def festival_factor(date, route):

    month = date.month
    day = date.day

    factor = 1.0

    # Diwali / festive travel
    if (month == 10 and day >= 18) or (month == 11 and day <= 5):

        if route in ["DEL-SXR", "BOM-GOI"]:
            factor += 0.35
        else:
            factor += 0.22

    # Christmas / New Year
    if (month == 12 and day >= 18) or (
        month == 1 and day <= 5
    ):
        factor += 0.20

    # Holi / spring festival travel
    if month == 3 and 10 <= day <= 31:
        factor += 0.17

    # Independence Day travel
    if month == 8 and 10 <= day <= 20:
        factor += 0.14

    # Summer vacation
    if month in [5, 6]:

        if route in ["DEL-SXR", "BOM-GOI"]:
            factor += 0.12
        else:
            factor += 0.05

    return factor


# ---------------------------------------------------------
# Short abnormal shocks
#
# These last only 2–3 days.
# They are NOT explicitly labelled in the dataset.
# ---------------------------------------------------------

shock_events = [
    # date, magnitude
    (datetime(2025, 11, 7), 0.40),
    (datetime(2026, 1, 14), 0.30),
    (datetime(2026, 4, 18), 0.42),
    (datetime(2026, 7, 9), 0.34),
    (datetime(2026, 8, 15), 0.46),
]


def temporary_shock(date):

    factor = 1.0

    for event_date, magnitude in shock_events:

        difference = (date - event_date).days

        # Event lasts 3 days
        if 0 <= difference <= 2:

            decay = 1 - (0.15 * difference)

            factor += magnitude * decay

    return factor


# ---------------------------------------------------------
# Generate data
#
# 300 days × 10 routes = 3000 records
# ---------------------------------------------------------

start_date = datetime(
    2025,
    9,
    15,
    tzinfo=timezone.utc
)

records = []

for day_number in range(300):

    current_date = start_date + timedelta(
        days=day_number
    )

    date_without_timezone = current_date.replace(
        tzinfo=None
    )

    # -----------------------------------------------------
    # Long-term fuel / macro trend
    # -----------------------------------------------------

    fuel_factor = (
        1.0
        + 0.00045 * day_number
        + 0.022
        * math.sin(
            2 * math.pi * day_number / 90
        )
    )

    # General market movement
    macro_factor = (
        1.0
        + 0.015
        * math.sin(
            2 * math.pi * day_number / 180
        )
    )

    for route_index, (origin, destination) in enumerate(routes):

        route = f"{origin}-{destination}"

        # -------------------------------------------------
        # Recurring festival pattern
        # -------------------------------------------------

        season_factor = festival_factor(
            date_without_timezone,
            route
        )

        # -------------------------------------------------
        # Weekly demand pattern
        # -------------------------------------------------

        weekday = current_date.weekday()

        weekly_factor = 1.0

        # Friday/Sunday demand
        if weekday in [4, 6]:
            weekly_factor += 0.045

        # Tuesday relatively lower
        if weekday == 1:
            weekly_factor -= 0.015

        # -------------------------------------------------
        # Temporary 2–3 day anomaly
        # -------------------------------------------------

        shock_factor = temporary_shock(
            date_without_timezone
        )

        # -------------------------------------------------
        # Route sensitivity
        # -------------------------------------------------

        if route in ["DEL-SXR", "BOM-GOI"]:
            capacity_sensitivity = 1.20
        else:
            capacity_sensitivity = 0.90

        # -------------------------------------------------
        # Lead time
        # -------------------------------------------------

        lead_days = random.choice([
            1,
            2,
            3,
            5,
            7,
            10,
            14,
            21,
            30
        ])

        # Flights closer to departure tend to cost more
        booking_factor = (
            1.0
            + 0.38
            * math.exp(
                -lead_days / 8
            )
        )

        # -------------------------------------------------
        # Random market noise
        # -------------------------------------------------

        noise = random.gauss(
            0,
            0.035
        )

        # -------------------------------------------------
        # Final fare
        # -------------------------------------------------

        price = route_base_price[route]

        price *= fuel_factor
        price *= macro_factor
        price *= season_factor
        price *= weekly_factor

        price *= (
            1
            + capacity_sensitivity
            * (shock_factor - 1)
        )

        price *= booking_factor

        price *= (
            1 + noise
        )

        # Avoid unrealistic values
        price = max(
            1800,
            price
        )

        # Round to realistic fare increments
        price = int(
            round(price / 10) * 10
        )

        # -------------------------------------------------
        # Flight information
        # -------------------------------------------------

        airline = random.choice(
            list(airlines.keys())
        )

        flight_code = airlines[airline]

        flight_number = (
            f"{flight_code}-"
            f"{random.randint(100,3999)}"
            f"ECONOMY"
        )

        departure_hour = random.choice([
            6,
            7,
            8,
            10,
            12,
            15,
            18,
            20
        ])

        departure_minute = random.choice([
            0,
            5,
            15,
            30,
            35,
            45
        ])

        duration = random.randint(
            *duration_range[route]
        )

        arrival_total = (
            departure_hour * 60
            + departure_minute
            + duration
        )

        arrival_hour = (
            arrival_total // 60
        ) % 24

        arrival_minute = (
            arrival_total % 60
        )

        stops = (
            "Non-stop"
            if random.random() < 0.91
            else "1 stop"
        )

        scraped_at = (
            current_date
            + timedelta(
                hours=random.randint(6, 18),
                minutes=random.randint(0, 59)
            )
        )

        # -------------------------------------------------
        # SAME schema as your real data
        # -------------------------------------------------

        record = {

            "airline": airline,

            "flight_number": flight_number,

            "departure_time":
                f"{departure_hour:02d}:"
                f"{departure_minute:02d}",

            "arrival_time":
                f"{arrival_hour:02d}:"
                f"{arrival_minute:02d}",

            "origin": origin,

            "destination": destination,

            "duration":
                f"{duration // 60:02d}h "
                f"{duration % 60:02d}m",

            "stops": stops,

            "price": price,

            "currency": "INR",

            "source_platform":
                random.choice(
                    source_platforms
                ),

            "lead_time":
                f"T+{lead_days}",

            "scraped_at":
                scraped_at.isoformat()
        }

        records.append(record)


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        records,
        file,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Created {len(records)} records"
)

print(
    f"Saved to: {OUTPUT}"
)
