"""Initial schema migration for PROMETHEUS

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-12 14:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. fare_observations
    op.create_table(
        'fare_observations',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('scraped_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_type', sa.String(length=32), nullable=False),
        sa.Column('source_name', sa.String(length=64), nullable=False),
        sa.Column('carrier_iata', sa.String(length=2), nullable=False),
        sa.Column('flight_number', sa.String(length=16), nullable=False),
        sa.Column('origin_iata', sa.String(length=3), nullable=False),
        sa.Column('destination_iata', sa.String(length=3), nullable=False),
        sa.Column('departure_date', sa.Date(), nullable=False),
        sa.Column('departure_time', sa.Time(), nullable=False),
        sa.Column('arrival_date', sa.Date(), nullable=False),
        sa.Column('arrival_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('stops', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cabin_class', sa.String(length=32), nullable=False, server_default='ECONOMY'),
        sa.Column('base_fare_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('taxes_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_fare_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('seats_available', sa.Integer(), nullable=True),
        sa.Column('scrape_url', sa.Text(), nullable=True),
        sa.Column('scraper_version', sa.String(length=16), nullable=True),
        sa.Column('raw_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fare_observations_carrier_iata'), 'fare_observations', ['carrier_iata'], unique=False)
    op.create_index(op.f('ix_fare_observations_departure_date'), 'fare_observations', ['departure_date'], unique=False)
    op.create_index(op.f('ix_fare_observations_destination_iata'), 'fare_observations', ['destination_iata'], unique=False)
    op.create_index(op.f('ix_fare_observations_origin_iata'), 'fare_observations', ['origin_iata'], unique=False)
    op.create_index(op.f('ix_fare_observations_raw_hash'), 'fare_observations', ['raw_hash'], unique=True)
    op.create_index(op.f('ix_fare_observations_scraped_at'), 'fare_observations', ['scraped_at'], unique=False)
    op.create_index(op.f('ix_fare_observations_total_fare_inr'), 'fare_observations', ['total_fare_inr'], unique=False)
    op.create_index('ix_fare_obs_route_dept', 'fare_observations', ['origin_iata', 'destination_iata', 'departure_date'], unique=False)

    # 2. route_indices
    op.create_table(
        'route_indices',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('index_date', sa.Date(), nullable=False),
        sa.Column('route_pair', sa.String(length=7), nullable=False),
        sa.Column('origin_iata', sa.String(length=3), nullable=False),
        sa.Column('destination_iata', sa.String(length=3), nullable=False),
        sa.Column('index_value', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False),
        sa.Column('mean_fare_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_fare_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('max_fare_inr', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_route_indices_calculated_at'), 'route_indices', ['calculated_at'], unique=False)
    op.create_index(op.f('ix_route_indices_index_date'), 'route_indices', ['index_date'], unique=False)
    op.create_index(op.f('ix_route_indices_route_pair'), 'route_indices', ['route_pair'], unique=False)

    # 3. airfare_indices
    op.create_table(
        'airfare_indices',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('index_date', sa.Date(), nullable=False),
        sa.Column('apix_value', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('economy_subindex', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('nonstop_subindex', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('total_routes_monitored', sa.Integer(), nullable=False),
        sa.Column('total_observations_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_airfare_indices_calculated_at'), 'airfare_indices', ['calculated_at'], unique=False)
    op.create_index(op.f('ix_airfare_indices_index_date'), 'airfare_indices', ['index_date'], unique=False)

    # 4. alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('rule_type', sa.String(length=32), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False),
        sa.Column('route_pair', sa.String(length=7), nullable=False),
        sa.Column('current_value', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('baseline_value', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('percentage_change', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_route_pair'), 'alerts', ['route_pair'], unique=False)
    op.create_index(op.f('ix_alerts_triggered_at'), 'alerts', ['triggered_at'], unique=False)

def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('airfare_indices')
    op.drop_table('route_indices')
    op.drop_table('fare_observations')
