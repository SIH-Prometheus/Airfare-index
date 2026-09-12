# PROMETHEUS — Master Build Progress Checklist

This file tracks the implementation status of all phases in the PROMETHEUS Real-time Airfare Price Index (APIx) build. Antigravity and human developers update this file as each phase completes its Definition of Done.

---

## Shared References
- [x] `docs/00-conventions.md` — Repo layout, naming, coding standards, env/config rules, git workflow
- [x] `docs/01-architecture.md` — Full system architecture, data flow, tech stack rationale

---

## Implementation Phases

### Priority Tier 1: MUST HAVE (Demoable Core Engine & MVP)
- [x] **Phase 00 — Foundation**: Repo layout, Pydantic Settings, CLI, Makefile, pyproject.toml (`docs/phases/phase-00-foundation.md`)
- [x] **Phase 01 — Data Model**: Canonical `FareObservation` schema & Pydantic contracts (`docs/phases/phase-01-data-model.md`)
- [ ] **Phase 02 — Scraping**: Playwright framework + IndiGo, MakeMyTrip, Air India scrapers (`docs/phases/phase-02-scraping.md`)
- [ ] **Phase 03 — Raw Storage**: MinIO object lake & compressed Parquet storage (`docs/phases/phase-03-raw-storage.md`)
- [ ] **Phase 04 — ETL**: Cleaning, normalisation, deduplication, quality gate engine (`docs/phases/phase-04-etl.md`)
- [ ] **Phase 05 — Database**: PostgreSQL schema, async SQLAlchemy ORM, Alembic migrations (`docs/phases/phase-05-database.md`)
- [ ] **Phase 06 — Index Engine**: Jevons geometric route index + DGCA passenger-weighted APIx (`docs/phases/phase-06-index-engine.md`)
- [ ] **Phase 07 — Dashboard**: FastAPI REST API + Next.js interactive UI dashboard (`docs/phases/phase-07-dashboard.md`)

### Priority Tier 2: YOUR USP (Advanced Analytics & Explainability)
- [ ] **Phase 08 — Basic Alerts**: Rule-based WoW % change & Z-score alert triggers (`docs/phases/phase-08-basic-alerts.md`)
- [ ] **Phase 09 — ML Anomaly**: Isolation Forest unsupervised fare anomaly detector (`docs/phases/phase-09-ml-anomaly.md`)
- [ ] **Phase 10 — Forecasting**: SARIMA & Prophet time-series fare index baseline forecaster (`docs/phases/phase-10-forecasting.md`)
- [ ] **Phase 11 — Explainability**: Route contribution engine & feature movement scoring (`docs/phases/phase-11-explainability.md`)

### Priority Tier 3: NICE TO HAVE (Automation)
- [ ] **Phase 12 — Automation**: Prefect 3 task scheduling & pipeline orchestration (`docs/phases/phase-12-automation.md`)

### Priority Tier 4: PRODUCTION-GRADE (Deployment & Security)
- [ ] **Phase 13 — Docker**: Multi-stage Dockerfiles & docker-compose reproducibility (`docs/phases/phase-13-docker.md`)
- [ ] **Phase 14 — Auth**: OAuth2 / OIDC & Role-Based Access Control (RBAC) (`docs/phases/phase-14-auth.md`)
- [ ] **Phase 15 — Production**: Prometheus telemetry, GitHub Actions CI/CD, deployment guide (`docs/phases/phase-15-production.md`)

---

## Current Status
- **Documentation Set**: 100% Complete (All 18 files created and verified).
- **Core Scaffold**: 100% Complete (`pyproject.toml`, `.env.example`, `Makefile`, package structure).
- **Completed Phases**: Phase 00 (Foundation) & Phase 01 (Data Model).
- **Next Phase**: Phase 02 (Scraping).
