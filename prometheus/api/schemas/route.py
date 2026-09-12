"""Pydantic v2 schemas for Route responses."""
from __future__ import annotations

from pydantic import BaseModel


class Route(BaseModel):
    id:          int
    origin:      str
    destination: str
    distance_km: float
    weight:      float

    model_config = {"from_attributes": True}


class RouteDetail(Route):
    current_index:  float
    wow_change:     float


class RouteListResponse(BaseModel):
    items: list[RouteDetail]
    total: int
