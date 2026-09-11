# Phase 05 — Database: PostgreSQL Schema & Access Layer

## Objective
Define SQLAlchemy 2.0 ORM models, repository patterns, and Alembic database migrations.

## Alignment with problem statement & feasibility
Provides reliable, relational OLTP storage for index values, alerts, and fare history.

## Prerequisites
Phase 04 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| SQLAlchemy | 2.0.30 | Async ORM |
| Alembic | 1.13.1 | Schema migrations |

## Repo layout after this phase
```
prometheus/db/
├── __init__.py
├── models.py
├── session.py
└── repository.py
```

## Implementation Steps
### Step 1: ORM Models in `prometheus/db/models.py`
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Numeric, DateTime, Integer
from datetime import datetime

class Base(DeclarativeBase):
    pass

class FareObservationORM(Base):
    __tablename__ = "fare_observations"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    carrier_iata: Mapped[str] = mapped_column(String(2), index=True)
    origin_iata: Mapped[str] = mapped_column(String(3), index=True)
    destination_iata: Mapped[str] = mapped_column(String(3), index=True)
    total_fare_inr: Mapped[float] = mapped_column(Numeric(10, 2))
    raw_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
```

## Deliverables
- `prometheus/db/models.py`
- `prometheus/db/session.py`
- `prometheus/db/repository.py`
- `alembic/versions/`
- `tests/unit/test_repository.py`

## Definition of Done
```bash
pytest tests/unit/test_repository.py
```

## Out of Scope
Multi-master database clustering.

## Notes
Always use asyncpg database driver.
