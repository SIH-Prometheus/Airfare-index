# 00 — Conventions & Standards

## 1. Project Overview & Repository Layout
PROMETHEUS (SIH26056) is a real-time Airfare Price Index (APIx) engine for India designed to augment the domestic Consumer Price Index (CPI). 

The repository structure follows a modular architecture separating data ingestion, processing, index computation, API presentation, analytics/ML, and UI layers:

```
Airfare-index/
├── .github/workflows/         # CI/CD pipelines (Phase 15)
├── alembic/                   # PostgreSQL schema migrations (Phase 05)
│   ├── versions/
│   └── env.py
├── docs/                      # Master Build Documentation
│   ├── phases/                # Phase specifications (00-15)
│   ├── 00-conventions.md       # Conventions and repository rules (this file)
│   └── 01-architecture.md      # Full architecture specification & design rationale
├── frontend/                  # Next.js 14 Dashboard UI (Phase 07)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── prometheus/                # Main Python Package
│   ├── __init__.py
│   ├── config.py              # Pydantic BaseSettings configuration (Phase 00)
│   ├── cli.py                 # Typer CLI interface (Phase 00)
│   ├── models/                # Pydantic schemas & data contracts (Phase 01)
│   ├── scrapers/              # Async web scraping framework & adapters (Phase 02)
│   │   ├── airlines/
│   │   └── ota/
│   ├── storage/               # Raw S3/MinIO & Parquet lake access (Phase 03)
│   ├── etl/                   # Cleaning, normalisation, deduplication, quality (Phase 04)
│   ├── db/                    # SQLAlchemy 2.0 database models & repositories (Phase 05)
│   ├── index/                 # Jevons & weighted APIx index computation engine (Phase 06)
│   ├── api/                   # FastAPI Web API application (Phase 07)
│   │   └── routers/
│   ├── alerts/                # Rule-based alert & notification engine (Phase 08)
│   ├── ml/                    # Isolation Forest anomaly detection & forecasting (Phases 09-11)
│   ├── orchestration/         # Prefect 3 flows & tasks (Phase 12)
│   ├── auth/                  # OAuth2 / OIDC / RBAC layer (Phase 14)
│   └── monitoring/            # Prometheus metrics & health probes (Phase 15)
├── scripts/                   # DB seeding and operations scripts
├── tests/                     # Test Suite (unit, integration, e2e)
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example               # Template for environment variables (Phase 00)
├── docker-compose.yml         # Container orchestration (Phase 13)
├── Dockerfile                 # Multi-stage container build for Python services (Phase 13)
├── Makefile                   # Developer task automation (Phase 00)
├── PROGRESS.md                # Phase completion checklist
└── pyproject.toml             # Project manifest and pinned dependencies (Phase 00)
```

---

## 2. Coding Standards & Conventions

### 2.1 Python Environment & Versions
- **Python Version**: `3.12+` strictly required.
- **Package Management**: `uv` or standard `pip` using explicit versions defined in `pyproject.toml`.

### 2.2 Formatting and Linting
- **Code Formatter**: `black` configured with line length `100`.
- **Linter & Import Sorter**: `ruff` with rules `["E", "W", "F", "I", "B", "C4", "UP"]`.
- **Type Annotations**: `mypy` strict mode enforced (`strict = true`). Every function signature must have explicit parameter types and return type annotations.

### 2.3 Naming Conventions
- **Modules / Packages**: `snake_case` (e.g., `fare_observation.py`, `jevons.py`).
- **Classes**: `PascalCase` (e.g., `BaseScraper`, `FareRepository`).
- **Variables & Functions**: `snake_case` (e.g., `calculate_jevons_index`, `raw_payload`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT_SECONDS`, `TOP_ROUTES`).
- **Route Pair Format**: IATA 3-letter origin and destination separated by a hyphen, strictly upper-case: `DEL-BOM`, `BOM-BLR`.
- **Airline / OTA Codes**: Official 2-letter IATA code for carriers (`6E`, `AI`, `IX`, `SG`, `QP`).

---

## 3. Configuration & Environment Management
- No secret or environment-specific setting may be hardcoded.
- Configuration is loaded via `prometheus.config.Settings`, backed by `pydantic-settings`.
- Environment variable prefix: `PROMETHEUS_`.
- All variables must be documented in `.env.example`.

---

## 4. Git & Branching Workflow
- **Main Branch**: `main` (always deployable and passing green checks).
- **Feature Branches**: `feat/phase-NN-<description>` (e.g., `feat/phase-02-scraping`).
- **Commit Messages**: `[PhaseNN] Action verb short summary` (e.g., `[Phase02] Implement IndiGo Playwright scraper`).
- **Tags**: When a phase passes its Definition of Done, tag the commit: `git tag phase-NN-done`.

---

## 5. Testing & Quality Standards
- **Framework**: `pytest` with `pytest-asyncio` for async tests.
- **Coverage Target**: Minimum `80%` code coverage required across all modules (`--cov-fail-under=80`).
- **Test Structure**:
  - `tests/unit/`: Standalone unit tests (no external databases, networks, or MinIO required).
  - `tests/integration/`: Integration tests against PostgreSQL, MinIO, or Redis containers.
  - `tests/e2e/`: Full pipeline end-to-end execution checks.

---

## 6. Structured Logging & Observability
- **Logging Library**: `structlog`.
- **Log Format**: JSON formatted in staging/production; colored key-value format in local development (`PROMETHEUS_ENV=development`).
- **Contextual Fields**: Always attach context like `route`, `source`, `scrape_id`, or `run_id` when logging pipeline operations.

---

## 7. Async Guidelines
- Async-first architecture using `asyncio` and `anyio`.
- All I/O operations (HTTP fetching via Playwright/httpx, DB queries via asyncpg, Redis calls, file read/write) must be non-blocking async operations.
