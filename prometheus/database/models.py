from datetime import datetime, date, time, timezone
from decimal import Decimal
from typing import Optional, Dict, Any
import uuid

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Numeric,
    Integer,
    Date,
    Time,
    DateTime,
    JSON,
    Index,
)

class Base(DeclarativeBase):
    pass

class FareObservationModel(Base):
    __tablename__ = "fare_observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_name: Mapped[str] = mapped_column(String(64), nullable=False)
    carrier_iata: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    flight_number: Mapped[str] = mapped_column(String(16), nullable=False)
    origin_iata: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    destination_iata: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    departure_time: Mapped[time] = mapped_column(Time, nullable=False)
    arrival_date: Mapped[date] = mapped_column(Date, nullable=False)
    arrival_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    stops: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cabin_class: Mapped[str] = mapped_column(String(32), nullable=False, default="ECONOMY")
    base_fare_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    taxes_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_fare_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    seats_available: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scrape_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    scraper_version: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, default="0.1.0")
    raw_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_fare_obs_route_dept", "origin_iata", "destination_iata", "departure_date"),
    )

class RouteIndexModel(Base):
    __tablename__ = "route_indices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    index_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    route_pair: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    origin_iata: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_iata: Mapped[str] = mapped_column(String(3), nullable=False)
    index_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_fare_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    min_fare_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_fare_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

class AirfareIndexModel(Base):
    __tablename__ = "airfare_indices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    index_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    apix_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    economy_subindex: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    nonstop_subindex: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    total_routes_monitored: Mapped[int] = mapped_column(Integer, nullable=False)
    total_observations_count: Mapped[int] = mapped_column(Integer, nullable=False)

class AlertModel(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    route_pair: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    current_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    baseline_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    percentage_change: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
