"""Pydantic v2 schemas for Airline and Airport responses."""
from __future__ import annotations

from pydantic import BaseModel


class Airline(BaseModel):
    id:        int
    code:      str
    name:      str
    iata_code: str

    model_config = {"from_attributes": True}


class Airport(BaseModel):
    id:      int
    code:    str
    city:    str
    country: str

    model_config = {"from_attributes": True}
