# Phase 02 — Scraping: Framework + Airline & OTA Scrapers

## Objective
Build the asynchronous web scraping framework using Playwright to ingest flight data from IndiGo, MakeMyTrip, and Air India.

## Alignment with problem statement & feasibility
Fulfills real-time data collection requirement across domestic airlines and OTAs.

## Prerequisites
Phase 01 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Playwright | 1.44.0 | Browser automation |
| Tenacity | 8.2.3 | Retry mechanisms |

## Repo layout after this phase
```
prometheus/scrapers/
├── __init__.py
├── base.py
├── airlines/
│   ├── indigo.py
│   └── airindia.py
└── ota/
    └── makemytrip.py
```

## Implementation Steps
### Step 1: Base Scraper Class `prometheus/scrapers/base.py`
```python
from abc import ABC, abstractmethod
from typing import List
from prometheus.models.fare import FareObservation
from playwright.async_api import async_playwright
import structlog

logger = structlog.get_logger()

class BaseScraper(ABC):
    def __init__(self, headless: bool = True):
        self.headless = headless

    @abstractmethod
    async def scrape_route(self, origin: str, destination: str, travel_date: str) -> List[FareObservation]:
        pass
```

## Deliverables
- `prometheus/scrapers/base.py`
- `prometheus/scrapers/airlines/indigo.py`
- `prometheus/scrapers/ota/makemytrip.py`
- `tests/unit/test_scrapers.py`

## Definition of Done
```bash
pytest tests/unit/test_scrapers.py
```

## Out of Scope
Captcha breaking services or residential proxy network integration.

## Notes
Always emulate standard desktop user agents.
