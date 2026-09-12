from datetime import date
from typing import Sequence, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from prometheus.models.fare import FareObservation, SourceType, CabinClass
from prometheus.models.index import RouteIndex, AirfareIndex
from prometheus.models.alert import Alert, AlertSeverity, AlertRuleType
from prometheus.database.models import (
    FareObservationModel,
    RouteIndexModel,
    AirfareIndexModel,
    AlertModel,
)

class FareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_fare_observation(self, obs: FareObservation) -> FareObservationModel:
        """Saves a single FareObservation Pydantic model to database."""
        db_model = FareObservationModel(
            scraped_at=obs.scraped_at,
            source_type=obs.source_type.value if isinstance(obs.source_type, SourceType) else str(obs.source_type),
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
            cabin_class=obs.cabin_class.value if isinstance(obs.cabin_class, CabinClass) else str(obs.cabin_class),
            base_fare_inr=obs.base_fare_inr,
            taxes_inr=obs.taxes_inr,
            total_fare_inr=obs.total_fare_inr,
            seats_available=obs.seats_available,
            scrape_url=obs.scrape_url,
            scraper_version=obs.scraper_version,
            raw_hash=obs.raw_hash,
        )
        self.session.add(db_model)
        await self.session.flush()
        return db_model

    async def save_fare_observations_batch(
        self, obs_list: Sequence[FareObservation]
    ) -> int:
        """Saves a list of FareObservation Pydantic models to database."""
        db_models = [
            FareObservationModel(
                scraped_at=obs.scraped_at,
                source_type=obs.source_type.value if isinstance(obs.source_type, SourceType) else str(obs.source_type),
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
                cabin_class=obs.cabin_class.value if isinstance(obs.cabin_class, CabinClass) else str(obs.cabin_class),
                base_fare_inr=obs.base_fare_inr,
                taxes_inr=obs.taxes_inr,
                total_fare_inr=obs.total_fare_inr,
                seats_available=obs.seats_available,
                scrape_url=obs.scrape_url,
                scraper_version=obs.scraper_version,
                raw_hash=obs.raw_hash,
            )
            for obs in obs_list
        ]
        self.session.add_all(db_models)
        await self.session.flush()
        return len(db_models)

    async def get_by_hash(self, raw_hash: str) -> Optional[FareObservationModel]:
        """Fetches a fare observation by its unique SHA-256 hash."""
        stmt = select(FareObservationModel).where(FareObservationModel.raw_hash == raw_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fares_for_route_and_date(
        self, origin_iata: str, destination_iata: str, departure_date: date
    ) -> Sequence[FareObservationModel]:
        """Fetches fare observations for a given origin, destination, and departure date."""
        stmt = select(FareObservationModel).where(
            FareObservationModel.origin_iata == origin_iata.upper(),
            FareObservationModel.destination_iata == destination_iata.upper(),
            FareObservationModel.departure_date == departure_date,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
