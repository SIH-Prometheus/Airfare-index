"""
routers/fares.py — Fare endpoints
  GET /api/fares
  GET /api/fares/stats
  GET /api/fares/{id}
"""
from __future__ import annotations

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from prometheus.api.schemas import FareListResponse, FareObservation, FareStats
from prometheus.api.seed import FARE_OBS, ROUTES

router = APIRouter(prefix="/api/fares", tags=["Fares"])


@router.get("/stats", response_model=list[FareStats])
async def get_fare_stats() -> list[FareStats]:
    """Aggregate fare statistics (avg, min, max) per route."""
    from collections import defaultdict

    route_buckets: dict[int, list[float]] = defaultdict(list)
    for fare in FARE_OBS:
        route_buckets[fare["route_id"]].append(fare["total_fare"])

    route_map = {r["id"]: r for r in ROUTES}
    stats: list[FareStats] = []
    for route_id, fares in route_buckets.items():
        r = route_map[route_id]
        stats.append(FareStats(
            route_id    = route_id,
            origin      = r["origin"],
            destination = r["destination"],
            avg_fare    = round(sum(fares) / len(fares), 2),
            min_fare    = round(min(fares), 2),
            max_fare    = round(max(fares), 2),
            count       = len(fares),
        ))
    return sorted(stats, key=lambda s: s.route_id)


@router.get("", response_model=FareListResponse)
async def list_fares(
    route_id:   Optional[int]  = Query(None, description="Filter by route ID"),
    airline:    Optional[str]  = Query(None, description="Filter by airline name"),
    start_date: Optional[date] = Query(None, description="Filter from observation date"),
    end_date:   Optional[date] = Query(None, description="Filter to observation date"),
    advance:    Optional[int]  = Query(None, description="Filter by advance days (1/7/15/30)"),
    page:       int            = Query(1,    ge=1),
    limit:      int            = Query(20,   ge=1, le=100),
) -> FareListResponse:
    """List fare observations with optional filters and pagination."""
    data = FARE_OBS

    if route_id   is not None: data = [f for f in data if f["route_id"] == route_id]
    if airline:                data = [f for f in data if airline.lower() in f["airline"].lower()]
    if start_date:             data = [f for f in data if f["observation_date"] >= start_date]
    if end_date:               data = [f for f in data if f["observation_date"] <= end_date]
    if advance    is not None: data = [f for f in data if f["advance_days"] == advance]

    total  = len(data)
    pages  = math.ceil(total / limit)
    offset = (page - 1) * limit
    page_data = data[offset : offset + limit]

    return FareListResponse(
        items = [FareObservation(**f) for f in page_data],
        total = total,
        page  = page,
        limit = limit,
        pages = pages,
    )


@router.get("/{fare_id}", response_model=FareObservation)
async def get_fare(fare_id: int) -> FareObservation:
    """Get a specific fare observation by ID."""
    for fare in FARE_OBS:
        if fare["id"] == fare_id:
            return FareObservation(**fare)
    raise HTTPException(status_code=404, detail=f"Fare {fare_id} not found")
