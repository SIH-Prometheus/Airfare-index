"""Pydantic v2 schemas for FareObservation responses."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class FareObservation(BaseModel):
    id:               int
    airline:          str
    airline_code:     str
    source:           str
    origin:           str
    destination:      str
    route_id:         int
    observation_date: date
    departure_date:   date
    advance_days:     int
    base_fare:        float
    taxes:            float
    total_fare:       float
    currency:         str = "INR"
    scraped_at:       datetime

    model_config = {"from_attributes": True}


class FareStats(BaseModel):
    route_id:    int
    origin:      str
    destination: str
    avg_fare:    float
    min_fare:    float
    max_fare:    float
    count:       int


class FareListResponse(BaseModel):
    items:  list[FareObservation]
    total:  int
    page:   int
    limit:  int
    pages:  int
