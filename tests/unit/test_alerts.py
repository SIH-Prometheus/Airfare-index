import pytest
from prometheus.alerts.rules import AlertRuleEngine
from prometheus.alerts.scoring import calculate_alert_score, get_alert_level
from prometheus.alerts.engine import AlertEngine

def test_wow_change():
    assert AlertRuleEngine.check_wow_change(130, 115) == pytest.approx(13.04, 0.01)
    assert AlertRuleEngine.check_wow_change(100, 0) == 0.0

def test_z_score():
    hist = [120, 121, 119, 122, 120, 121, 123]
    # mean = ~120.857, std = ~1.245
    z = AlertRuleEngine.calculate_z_score(135, hist)
    assert z > 3.0 # Very unusual as per prompt
    
    assert AlertRuleEngine.calculate_z_score(100, [100]) == 0.0

def test_alert_scoring():
    # Example from prompt:
    # Alert Score = 0.30*WoW + 0.20*Z-score + 0.35*ML + 0.15*Forecast
    score = calculate_alert_score(12.0, 2.7, 0.94, 7.2)
    assert 0 <= score <= 1.0
    level = get_alert_level(score)
    assert level in ["NORMAL", "WATCH", "ELEVATED", "HIGH"]

def test_alert_engine():
    res = AlertEngine.generate_alert(
        current_apix=135.0,
        historical_apix=[120, 121, 119, 122, 120, 121, 123],
        route_contributions={"DEL-BOM": 4.8, "DEL-BLR": 3.1},
        lead_time_pressure={"T+1": 21.4, "T+7": 10.2},
        ml_anomaly_score=0.91,
        forecast_deviation=7.0
    )
    
    assert res["severity"] == "HIGH"
    assert "Near-term fares" in res["message"]
    assert len(res["contributors_detail"]) == 2
