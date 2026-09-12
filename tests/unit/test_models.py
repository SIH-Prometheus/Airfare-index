from datetime import date, time, datetime
from decimal import Decimal
from prometheus.models import FareObservation, SourceType, CabinClass, RouteIndex, AirfareIndex, Alert, AlertSeverity, AlertRuleType

def test_fare_observation_valid_creation():
    obs = FareObservation(
        scraped_at=datetime.utcnow(),
        source_type=SourceType.AIRLINE_DIRECT,
        source_name="IndiGo",
        carrier_iata="6e",
        flight_number="6E-204",
        origin_iata="del",
        destination_iata="bom",
        departure_date=date(2026, 10, 1),
        departure_time=time(10, 30),
        arrival_date=date(2026, 10, 1),
        arrival_time=time(12, 45),
        duration_minutes=135,
        stops=0,
        cabin_class=CabinClass.ECONOMY,
        base_fare_inr=Decimal("4500.00"),
        taxes_inr=Decimal("850.00"),
        total_fare_inr=Decimal("5350.00")
    )
    assert obs.carrier_iata == "6E"
    assert obs.origin_iata == "DEL"
    assert obs.destination_iata == "BOM"
    assert obs.route_pair == "DEL-BOM"
    assert len(obs.raw_hash) == 64

def test_route_index_creation():
    idx = RouteIndex(
        calculated_at=datetime.utcnow(),
        index_date=date(2026, 9, 11),
        route_pair="del-bom",
        origin_iata="del",
        destination_iata="bom",
        index_value=105.4,
        sample_size=42,
        mean_fare_inr=5200.0,
        min_fare_inr=3800.0,
        max_fare_inr=8900.0
    )
    assert idx.route_pair == "DEL-BOM"
    assert idx.index_value == 105.4

def test_alert_model():
    alert = Alert(
        triggered_at=datetime.utcnow(),
        rule_type=AlertRuleType.WOW_PERCENT_CHANGE,
        severity=AlertSeverity.HIGH,
        route_pair="DEL-BLR",
        current_value=122.5,
        baseline_value=100.0,
        percentage_change=22.5,
        message="Route DEL-BLR experienced a 22.5% WoW price spike."
    )
    assert alert.severity == AlertSeverity.HIGH
    assert alert.percentage_change == 22.5
