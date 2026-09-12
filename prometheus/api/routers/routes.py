"""
routers/routes.py — Route endpoints
  GET /api/routes
  GET /api/routes/{origin}/{destination}
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from prometheus.api.schemas import RouteDetail, RouteListResponse
from prometheus.api.seed import ROUTES, ROUTE_INDEX

router = APIRouter(prefix="/api/routes", tags=["Routes"])


def _route_current_index(route_id: int) -> tuple[float, float]:
    """Return (current_index, wow_change) for a route."""
    data = sorted(
        [r for r in ROUTE_INDEX if r["route_id"] == route_id],
        key=lambda r: r["date"],
    )
    if not data:
        return 100.0, 0.0
    latest   = data[-1]["index_value"]
    week_ago = data[-8]["index_value"] if len(data) >= 8 else data[0]["index_value"]
    wow      = round((latest - week_ago) / week_ago * 100, 2)
    return latest, wow


@router.get("", response_model=RouteListResponse)
async def list_routes() -> RouteListResponse:
    """List all routes with their current index values."""
    items = []
    for route in ROUTES:
        current, wow = _route_current_index(route["id"])
        items.append(RouteDetail(
            **route,
            current_index = current,
            wow_change    = wow,
        ))
    return RouteListResponse(items=items, total=len(items))


@router.get("/{origin}/{destination}", response_model=RouteDetail)
async def get_route(origin: str, destination: str) -> RouteDetail:
    """Get a specific route by origin/destination IATA codes."""
    origin      = origin.upper()
    destination = destination.upper()

    for route in ROUTES:
        if route["origin"] == origin and route["destination"] == destination:
            current, wow = _route_current_index(route["id"])
            return RouteDetail(**route, current_index=current, wow_change=wow)

    raise HTTPException(
        status_code=404,
        detail=f"Route {origin}→{destination} not found",
    )
