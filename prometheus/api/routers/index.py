"""
routers/index.py — Index endpoints
  GET /api/index/current
  GET /api/index/history
  GET /api/index/route/{route_id}
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from prometheus.api.schemas import (
    IndexCurrentResponse,
    IndexHistoryResponse,
    IndexValue,
)
from prometheus.api.seed import INDEX_HISTORY, ROUTE_INDEX

router = APIRouter(prefix="/api/index", tags=["Index"])


@router.get("/current", response_model=IndexCurrentResponse)
async def get_current_index() -> IndexCurrentResponse:
    """Return the latest APIx value with WoW and MoM changes."""
    if not INDEX_HISTORY:
        raise HTTPException(status_code=503, detail="No index data available")

    latest     = INDEX_HISTORY[-1]
    week_ago   = INDEX_HISTORY[-8]  if len(INDEX_HISTORY) >= 8  else INDEX_HISTORY[0]
    month_ago  = INDEX_HISTORY[-31] if len(INDEX_HISTORY) >= 31 else INDEX_HISTORY[0]

    wow = round((latest["index_value"] - week_ago["index_value"])  / week_ago["index_value"]  * 100, 2)
    mom = round((latest["index_value"] - month_ago["index_value"]) / month_ago["index_value"] * 100, 2)

    return IndexCurrentResponse(
        date        = latest["date"],
        index_value = latest["index_value"],
        index_type  = "APIx",
        wow_change  = wow,
        mom_change  = mom,
    )


@router.get("/history", response_model=IndexHistoryResponse)
async def get_index_history(
    start_date: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end_date:   Optional[date] = Query(None, description="End date YYYY-MM-DD"),
) -> IndexHistoryResponse:
    """Return APIx history optionally filtered by date range."""
    data = INDEX_HISTORY

    if start_date:
        data = [r for r in data if r["date"] >= start_date]
    if end_date:
        data = [r for r in data if r["date"] <= end_date]

    items = [IndexValue(**r) for r in data]
    return IndexHistoryResponse(
        items      = items,
        start_date = data[0]["date"]  if data else date.today(),
        end_date   = data[-1]["date"] if data else date.today(),
        total      = len(items),
    )


@router.get("/route/{route_id}", response_model=IndexHistoryResponse)
async def get_route_index(
    route_id:   int,
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
) -> IndexHistoryResponse:
    """Return index history for a specific route."""
    data = [r for r in ROUTE_INDEX if r["route_id"] == route_id]

    if not data:
        raise HTTPException(status_code=404, detail=f"Route {route_id} not found")

    if start_date:
        data = [r for r in data if r["date"] >= start_date]
    if end_date:
        data = [r for r in data if r["date"] <= end_date]

    items = [IndexValue(**r) for r in data]
    return IndexHistoryResponse(
        items      = items,
        start_date = data[0]["date"]  if data else date.today(),
        end_date   = data[-1]["date"] if data else date.today(),
        total      = len(items),
    )
