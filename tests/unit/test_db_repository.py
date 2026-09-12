from datetime import date, time, datetime, timezone
from decimal import Decimal
import pytest
from prometheus.models.fare import FareObservation, SourceType, CabinClass
from prometheus.db.models import FareObservationModel
from prometheus.db.repository import FareRepository

def test_fare_observation_to_orm_model_mapping():
    obs = FareObservation(
        scraped_at=datetime.now(timezone.utc),
        source_type=SourceType.AIRLINE_DIRECT,
        source_name="IndiGo",
        carrier_iata="6e",
        flight_number="6E-204",
        origin_iata="DEL",
        destination_iata="BOM",
        departure_date=date(2026, 10, 1),
        departure_time=time(10, 30),
        arrival_date=date(2026, 10, 1),
        arrival_time=time(12, 45),
        duration_minutes=135,
        stops=0,
        cabin_class=CabinClass.ECONOMY,
        base_fare_inr=Decimal("4500.00"),
        taxes_inr=Decimal("850.00"),
        total_fare_inr=Decimal("5350.00"),
    )
    db_model = FareObservationModel(
        scraped_at=obs.scraped_at,
        source_type=obs.source_type.value,
        source_name=obs.source_name,
        carrier_iata=obs.carrier_iata,
        flight_number=obs.flight_number,
        origin_iata=obs.origin_iata,
        destination_iata=obs.destination_iata,
        departure_date=obs.departure_date,
        departure_time=obs.departure_time,
        arrival_date=obs.arrival_date,
        arrival_time=obs.arrival_time,
        duration_minutes=obs.duration_minutes,
        stops=obs.stops,
        cabin_class=obs.cabin_class.value,
        base_fare_inr=obs.base_fare_inr,
        taxes_inr=obs.taxes_inr,
        total_fare_inr=obs.total_fare_inr,
        raw_hash=obs.raw_hash,
    )
    assert db_model.carrier_iata == "6E"
    assert db_model.total_fare_inr == Decimal("5350.00")
    assert db_model.raw_hash == obs.raw_hash
