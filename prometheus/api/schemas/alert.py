"""Pydantic v2 schemas for Alert responses."""
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Dict

from pydantic import BaseModel


class ContributorDetail(BaseModel):
    route: str
    contribution: float


class Alert(BaseModel):
    id:            int
    severity:      str          # NORMAL | WATCH | ELEVATED | HIGH
    score:         float
    wow_change:    float
    z_score:       float
    anomaly_score: float
    apix_value:    float
    contributors:  list[int]    # route IDs (legacy/simple)
    created_at:    datetime

    model_config = {"from_attributes": True}


class AlertCurrentResponse(BaseModel):
    severity:      str
    score:         float
    wow_change:    float
    z_score:       float
    anomaly_score: float
    forecast_deviation: float
    apix_value:    float
    message:       str
    contributors_detail: List[ContributorDetail]
    lead_time_pressure: Dict[str, float]
    created_at:    datetime


class AlertHistoryResponse(BaseModel):
    items: list[Alert]
    total: int
