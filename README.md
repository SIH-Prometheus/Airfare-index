# PROMETHEUS MVP — Quick Start

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose)
- That's it — no Python or Node.js installation needed

## Run the full stack

```powershell
# From the repo root
docker compose up --build
```

Wait ~60 seconds for all services to initialize, then open:

| Service | URL |
|---|---|
| 🌐 Frontend Dashboard | http://localhost:3000 |
| 🔧 API Swagger | http://localhost:8000/docs |
| 🗄 MinIO Console | http://localhost:9001 (minioadmin / minioadmin) |
| ❤️ Health Check | http://localhost:8000/health |

## Using the Dashboard

1. Open http://localhost:3000
2. Click **Launch App** on the landing page
3. Click **✦ Refresh Fares** to run the full pipeline:
   - Scraper attempts live Google Flights fetch (httpx, best-effort)
   - Falls back to `data/sample/DEL_BOM_sample.json` if blocked
   - Uploads raw JSON to MinIO bucket `airfare-data`
   - ETL validates + deduplicates + inserts into PostgreSQL
   - Airfare Index calculated: `APIx = avg_fare / 4500 × 100`
   - Dashboard updates with cards, chart, and airline table

## MVP API Endpoints

```
POST /api/scrape?origin=DEL&destination=BOM   — trigger full pipeline
GET  /api/airfare-index?origin=DEL&destination=BOM   — current index
GET  /api/airfare-index/trend?origin=DEL&destination=BOM   — trend data
GET  /api/flights?origin=DEL&destination=BOM   — flight records
GET  /health   — service health
GET  /docs     — Swagger UI
```

## Local Development (without Docker)

### Backend

```powershell
# Requires: PostgreSQL + MinIO running locally
pip install -r requirements.txt

# Set environment
copy .env.example .env
# Edit .env as needed

uvicorn prometheus.api.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

## Architecture

```
Browser (localhost:3000)
    │
    │ HTTP/JSON (NEXT_PUBLIC_API_URL)
    ▼
Next.js Dashboard (frontend container)
    │
    │ POST /api/scrape
    ▼
FastAPI Backend (backend container, port 8000)
    │
    ├─► httpx scraper ──► Google Flights (best-effort)
    │                         │ (fails) ▼
    │                     data/sample/DEL_BOM_sample.json
    │
    ├─► MinIO (minio:9000) ── bucket: airfare-data
    │       Raw JSON stored at raw/YYYY-MM-DD/DEL_BOM_<ts>.json
    │
    ├─► ETL (validate + normalise + deduplicate)
    │
    ├─► PostgreSQL (postgres:5432, db: airfare)
    │       Tables: flights, airfare_index
    │
    └─► Index Calculator: APIx = avg_fare / 4500 × 100
            │
            └─► Response → Next.js Dashboard
```

## Scope

- **In scope**: DEL → BOM only (MVP)
- **Excluded from MVP**: ML/forecasting models (files remain, not executed)
- **Phase 2 extension points**: marked with comments in code

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TailwindCSS, ECharts, Axios |
| Backend | FastAPI, Python 3.12, SQLAlchemy (async) |
| Scraper | httpx (MVP), Scrapy+Playwright (full stack) |
| Storage | MinIO (S3-compatible object store) |
| Database | PostgreSQL 16 |
| Orchestration | Docker Compose |

## Project Structure

```
Airfare-index/
├── docker-compose.yml          ← orchestrate all services
├── Dockerfile.backend          ← FastAPI image
├── Dockerfile.frontend         ← Next.js image
├── requirements.backend.txt    ← lean Docker requirements
├── requirements.txt            ← full local dev requirements
├── .env                        ← local environment vars
├── .env.example                ← documented template
├── data/sample/
│   └── DEL_BOM_sample.json     ← fallback data (25 flights)
├── prometheus/
│   ├── api/
│   │   ├── main.py             ← FastAPI app + lifespan
│   │   └── routers/
│   │       └── mvp.py          ← /api/scrape, /api/airfare-index, etc.
│   ├── config.py               ← settings via env vars
│   ├── database/
│   │   ├── models.py           ← SQLAlchemy ORM models
│   │   └── session.py          ← async session management
│   ├── etl/
│   │   └── pipeline.py         ← validate → clean → deduplicate → insert
│   ├── index/
│   │   └── calculator.py       ← APIx = avg/baseline × 100
│   ├── scrapers/
│   │   └── runner.py           ← httpx scrape + MinIO upload
│   └── storage/
│       └── minio_client.py     ← MinIO SDK wrapper
└── frontend/
    ├── app/
    │   ├── page.tsx            ← landing page (existing)
    │   └── app/
    │       └── page.tsx        ← MVP dashboard (new)
    ├── services/
    │   └── api.ts              ← typed axios API client
    └── types/
        └── index.ts            ← TypeScript interfaces
```
