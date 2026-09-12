# Phase 01 — Data Model: Canonical FareObservation Schema & Pydantic Contracts

## Objective
Define the strict data contracts and validation rules governing every airfare observation captured across all airlines and OTAs.

## Alignment with problem statement & feasibility
Ensures standardized data capture across diverse source APIs and web DOM structures.

## Prerequisites
Phase 00 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Pydantic | 2.7.1 | Data validation & schemas |

## Repo layout after this phase
```
prometheus/models/
├── __init__.py
├── fare.py
├── index.py
└── alert.py
``` 

## Implementation Steps
### Step 1: Create `prometheus/models/fare.py`
```python
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class SourceType(str, Enum):
    AIRLINE_DIRECT = "AIRLINE_DIRECT"
    OTA = "OTA"

class CabinClass(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"

class FareObservation(BaseModel):
    scraped_at: datetime
    source_type: SourceType
    source_name: str
    carrier_iata: str = Field(min_length=2, max_length=2)
    flight_number: str
    origin_iata: str = Field(min_length=3, max_length=3)
    destination_iata: str = Field(min_length=3, max_length=3)
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    duration_minutes: int
    stops: int = 0
    cabin_class: CabinClass = CabinClass.ECONOMY
    base_fare_inr: Decimal
    taxes_inr: Decimal
    total_fare_inr: Decimal
    seats_available: Optional[int] = None
    raw_hash: str

    @field_validator("origin_iata", "destination_iata")
    def upper_iata(cls, v: str) -> str:
        return v.upper()
```

## Deliverables
- `prometheus/models/fare.py`
- `prometheus/models/index.py`
- `prometheus/models/alert.py`
- `tests/unit/test_models.py`

## Definition of Done
```bash 
pytest tests/unit/test_models.py
```

## Out of Scope
Database tables and ORM mappings (handled in Phase 05).

## Notes
Fares must always be denominated in INR.
