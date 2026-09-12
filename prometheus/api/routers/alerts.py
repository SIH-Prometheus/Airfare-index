"""
routers/alerts.py — Alert endpoints
  GET /api/alerts/current
  GET /api/alerts/history
  GET /api/alerts/{alert_id}
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from prometheus.api.schemas import Alert, AlertCurrentResponse, AlertHistoryResponse
from prometheus.api.seed import ALERTS, INDEX_HISTORY
from prometheus.alerts.engine import AlertEngine

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/current", response_model=AlertCurrentResponse)
async def get_current_alert() -> AlertCurrentResponse:
    """Return the dynamically computed most recent alert status."""
    if not INDEX_HISTORY:
        raise HTTPException(status_code=503, detail="No index data available")
    
    historical_apix = [x["index_value"] for x in INDEX_HISTORY]
    current_apix = historical_apix[-1]
    
    # Mock data for explainability (in a real system this comes from ETL/ML)
    route_contributions = {
        "DEL-BOM": 4.8,
        "DEL-BLR": 3.1,
        "BOM-BLR": 2.4,
        "DEL-MAA": 1.2,
        "HYD-DEL": 1.2
    }
    
    lead_time_pressure = {
        "T+1": 21.4,
        "T+7": 10.2,
        "T+15": 4.3,
        "T+30": 1.8
    }
    
    alert_data = AlertEngine.generate_alert(
        current_apix=current_apix,
        historical_apix=historical_apix,
        route_contributions=route_contributions,
        lead_time_pressure=lead_time_pressure,
        ml_anomaly_score=0.91,
        forecast_deviation=7.0
    )
    
    return AlertCurrentResponse(**alert_data)


@router.get("/history", response_model=AlertHistoryResponse)
async def get_alert_history(
    severity:   Optional[str]  = Query(None, description="NORMAL|WATCH|ELEVATED|HIGH"),
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
) -> AlertHistoryResponse:
    """Return historical alerts with optional filters."""
    data = ALERTS

    if severity:
        data = [a for a in data if a["severity"].upper() == severity.upper()]
    if start_date:
        data = [a for a in data if a["created_at"].date() >= start_date]
    if end_date:
        data = [a for a in data if a["created_at"].date() <= end_date]

    return AlertHistoryResponse(
        items = [Alert(**a) for a in data],
        total = len(data),
    )


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: int) -> Alert:
    """Get a specific alert by ID."""
    for alert in ALERTS:
        if alert["id"] == alert_id:
            return Alert(**alert)
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
