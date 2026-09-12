"""
routers/metadata.py — Reference data endpoints
  GET /api/airlines
  GET /api/airports
"""
from __future__ import annotations

from fastapi import APIRouter

from prometheus.api.schemas import Airline, Airport
from prometheus.api.seed import AIRLINES, AIRPORTS

router = APIRouter(prefix="/api", tags=["Metadata"])


@router.get("/airlines", response_model=list[Airline])
async def list_airlines() -> list[Airline]:
    """Return all supported airlines."""
    return [Airline(**a) for a in AIRLINES]


@router.get("/airports", response_model=list[Airport])
async def list_airports() -> list[Airport]:
    """Return all supported airports."""
    return [Airport(**a) for a in AIRPORTS]
