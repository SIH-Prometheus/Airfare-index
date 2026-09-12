from datetime import datetime, time

from pydantic import BaseModel, field_validator


class FlightRecord(BaseModel):

    airline: str
    flight_number: str
    departure_time: time
    arrival_time: time
    origin: str
    destination: str
    duration: str
    stops: str
    price: float
    currency: str
    source_platform: str
    lead_time: str
    scraped_at: datetime

    # --------------------------------------------------------
    # TEXT FIELDS
    # --------------------------------------------------------

    @field_validator(
        "airline",
        "flight_number",
        "duration",
        "currency",
        "source_platform"
    )
    @classmethod
    def clean_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    # --------------------------------------------------------
    # AIRPORT CODES
    # --------------------------------------------------------

    @field_validator("origin", "destination")
    @classmethod
    def validate_airport_code(cls, value):

        value = value.strip().upper()

        if len(value) != 3 or not value.isalpha():
            raise ValueError(
                "Airport code must contain exactly 3 letters"
            )

        return value

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):

        if value <= 0:
            raise ValueError(
                "Price must be greater than zero"
            )

        return value

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value):

        value = value.strip().upper()

        if value != "INR":
            raise ValueError(
                "Currency must be INR"
            )

        return value

    # --------------------------------------------------------
    # STOPS
    # --------------------------------------------------------

    @field_validator("stops")
    @classmethod
    def validate_stops(cls, value):

        value = value.strip().lower()

        allowed_stops = [
            "non-stop",
            "1 stop",
            "2 stops",
            "3 stops",
            "4 stops"
        ]

        if value not in allowed_stops:
            raise ValueError(
                f"Invalid stops value: {value}"
            )

        return value

    # --------------------------------------------------------
    # LEAD TIME
    # --------------------------------------------------------

    @field_validator("lead_time")
    @classmethod
    def validate_lead_time(cls, value):

        value = value.strip().upper()

        if not value.startswith("T+"):
            raise ValueError(
                "Lead time must be in format T+number"
            )

        try:
            days = int(value[2:])
        except ValueError:
            raise ValueError(
                "Lead time must be in format T+number"
            )

        if days < 0:
            raise ValueError(
                "Lead time cannot be negative"
            )

        return value