from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import hashlib
from pydantic import BaseModel, Field, field_validator, model_validator

class SourceType(str, Enum):
    AIRLINE_DIRECT = "AIRLINE_DIRECT"
    OTA = "OTA"

class CabinClass(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"

class FareObservation(BaseModel):
    scraped_at: datetime
    source_type: SourceType
    source_name: str
    carrier_iata: str = Field(..., min_length=2, max_length=2, description="2-letter IATA carrier code")
    flight_number: str
    origin_iata: str = Field(..., min_length=3, max_length=3, description="3-letter IATA origin airport code")
    destination_iata: str = Field(..., min_length=3, max_length=3, description="3-letter IATA destination airport code")
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    duration_minutes: int = Field(..., ge=1, description="Flight duration in minutes")
    stops: int = Field(default=0, ge=0, description="Number of intermediate stops")
    cabin_class: CabinClass = CabinClass.ECONOMY
    base_fare_inr: Decimal = Field(..., ge=0, description="Base fare in INR")
    taxes_inr: Decimal = Field(..., ge=0, description="Taxes and surcharges in INR")
    total_fare_inr: Decimal = Field(..., ge=0, description="Total fare in INR")
    seats_available: Optional[int] = Field(default=None, ge=1, description="Seats remaining if specified")
    scrape_url: str = Field(default="", description="Source URL queried")
    scraper_version: str = Field(default="0.1.0", description="Version of scraper script")
    raw_hash: str = Field(default="", description="SHA-256 hash of raw payload")

    @field_validator("carrier_iata", "origin_iata", "destination_iata")
    @classmethod
    def upper_codes(cls, v: str) -> str:
        return v.upper().strip()

    @model_validator(mode="after")
    def validate_total_fare_and_hash(self) -> "FareObservation":
        # Compute SHA-256 hash if empty
        if not self.raw_hash:
            raw_str = f"{self.source_name}:{self.carrier_iata}:{self.flight_number}:{self.origin_iata}:{self.destination_iata}:{self.departure_date}:{self.departure_time}"
            self.raw_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        return self

    @property
    def route_pair(self) -> str:
        """Returns standard route pair representation e.g. DEL-BOM."""
        return f"{self.origin_iata}-{self.destination_iata}"
