from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator

class RouteIndex(BaseModel):
    calculated_at: datetime
    index_date: date
    route_pair: str = Field(..., description="Route pair code e.g. DEL-BOM")
    origin_iata: str = Field(..., min_length=3, max_length=3)
    destination_iata: str = Field(..., min_length=3, max_length=3)
    index_value: float = Field(..., ge=0.0, description="Jevons route index relative to base period (Base = 100)")
    sample_size: int = Field(..., ge=1, description="Number of fare observations used")
    mean_fare_inr: float = Field(..., ge=0.0, description="Arithmetic mean fare in INR")
    min_fare_inr: float = Field(..., ge=0.0, description="Minimum fare observed in INR")
    max_fare_inr: float = Field(..., ge=0.0, description="Maximum fare observed in INR")

    @field_validator("route_pair", "origin_iata", "destination_iata")
    @classmethod
    def upper_codes(cls, v: str) -> str:
        return v.upper().strip()

class AirfareIndex(BaseModel):
    calculated_at: datetime
    index_date: date
    apix_value: float = Field(..., ge=0.0, description="National Airfare Price Index (APIx) value")
    economy_subindex: float = Field(..., ge=0.0, description="Economy-only sub-index value")
    nonstop_subindex: float = Field(..., ge=0.0, description="Nonstop-only sub-index value")
    total_routes_monitored: int = Field(..., ge=1)
    total_observations_count: int = Field(..., ge=1)
    route_weights: Dict[str, float] = Field(default_factory=dict, description="DGCA pax-volume weights by route")
