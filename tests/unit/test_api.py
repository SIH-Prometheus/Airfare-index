"""
tests/unit/test_api.py — Phase 7 API unit tests using TestClient.
Run: pytest tests/unit/test_api.py -v
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from prometheus.api.main import app

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("ok", "degraded")
    assert r.json()["phase"]  == "07"


# ── Index endpoints ───────────────────────────────────────────────────────────────

def test_index_current():
    r = client.get("/api/index/current")
    assert r.status_code == 200
    data = r.json()
    assert "index_value" in data
    assert "wow_change"  in data
    assert "mom_change"  in data
    assert data["index_type"] == "APIx"


def test_index_history_default():
    r = client.get("/api/index/history")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 90
    assert len(data["items"]) == 90


def test_index_history_date_filter():
    r = client.get("/api/index/history?start_date=2025-01-01")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 0          # depends on seed date


def test_route_index():
    r = client.get("/api/index/route/1")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 90


def test_route_index_not_found():
    r = client.get("/api/index/route/999")
    assert r.status_code == 404


# ── Fares endpoints ───────────────────────────────────────────────────────────────

def test_fares_list():
    r = client.get("/api/fares")
    assert r.status_code == 200
    data = r.json()
    assert data["total"]  == 300
    assert len(data["items"]) == 20    # default page size
    assert data["page"]  == 1


def test_fares_pagination():
    r = client.get("/api/fares?page=2&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 10
    assert data["page"] == 2


def test_fares_filter_airline():
    r = client.get("/api/fares?airline=IndiGo")
    assert r.status_code == 200
    data = r.json()
    for item in data["items"]:
        assert "IndiGo" in item["airline"]


def test_fares_stats():
    r = client.get("/api/fares/stats")
    assert r.status_code == 200
    stats = r.json()
    assert len(stats) == 5
    for s in stats:
        assert s["min_fare"] <= s["avg_fare"] <= s["max_fare"]


def test_fare_by_id():
    r = client.get("/api/fares/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_fare_not_found():
    r = client.get("/api/fares/9999")
    assert r.status_code == 404


# ── Routes endpoints ──────────────────────────────────────────────────────────────

def test_routes_list():
    r = client.get("/api/routes")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_route_detail():
    r = client.get("/api/routes/DEL/BOM")
    assert r.status_code == 200
    data = r.json()
    assert data["origin"]      == "DEL"
    assert data["destination"] == "BOM"
    assert "current_index" in data


def test_route_not_found():
    r = client.get("/api/routes/XYZ/ABC")
    assert r.status_code == 404


# ── Alerts endpoints ──────────────────────────────────────────────────────────────

def test_current_alert():
    r = client.get("/api/alerts/current")
    assert r.status_code == 200
    data = r.json()
    assert data["severity"] in {"NORMAL", "WATCH", "ELEVATED", "HIGH"}
    assert "score"     in data
    assert "wow_change" in data
    assert "message"    in data
    assert "contributors_detail" in data
    assert "lead_time_pressure" in data


def test_alert_history():
    r = client.get("/api/alerts/history")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0


def test_alert_filter_severity():
    r = client.get("/api/alerts/history?severity=NORMAL")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["severity"] == "NORMAL"


def test_alert_by_id():
    r = client.get("/api/alerts/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


# ── Metadata endpoints ────────────────────────────────────────────────────────────

def test_airlines():
    r = client.get("/api/airlines")
    assert r.status_code == 200
    airlines = r.json()
    assert len(airlines) == 3
    names = {a["name"] for a in airlines}
    assert "IndiGo" in names


def test_airports():
    r = client.get("/api/airports")
    assert r.status_code == 200
    airports = r.json()
    assert len(airports) == 6
    codes = {a["code"] for a in airports}
    assert "DEL" in codes
    assert "BOM" in codes
