"""Pydantic v2 schemas for IndexValue responses."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class IndexValue(BaseModel):
    id:          int
    date:        date
    index_value: float
    index_type:  str
    route_id:    Optional[int] = None

    model_config = {"from_attributes": True}


class IndexCurrentResponse(BaseModel):
    date:        date
    index_value: float
    index_type:  str = "APIx"
    wow_change:  float          # week-over-week % change
    mom_change:  float          # month-over-month % change


class IndexHistoryResponse(BaseModel):
    items:      list[IndexValue]
    start_date: date
    end_date:   date
    total:      int
