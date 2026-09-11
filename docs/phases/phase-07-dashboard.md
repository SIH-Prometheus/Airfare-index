# Phase 07 — Dashboard: FastAPI Web API & Next.js UI (MVP)

## Objective
Build the user presentation layer consisting of REST endpoints and an interactive React dashboard for visualization.

## Alignment with problem statement & feasibility
Delivers the MVP product interface for stakeholders and evaluation judges.

## Prerequisites
Phase 06 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| FastAPI | 0.111.0 | RESTful API engine |
| Next.js | 14.0 | Interactive React frontend |

## Repo layout after this phase
```
prometheus/api/
├── __init__.py
├── main.py
└── routers/
frontend/
├── app/
└── package.json
```

## Implementation Steps
### Step 1: FastAPI App in `prometheus/api/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PROMETHEUS Airfare Price Index API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "prometheus-api"}
```

## Deliverables
- `prometheus/api/main.py`
- `prometheus/api/routers/index.py`
- `frontend/app/page.tsx`
- `tests/unit/test_api.py`

## Definition of Done
```bash
pytest tests/unit/test_api.py
```

## Out of Scope
Mobile application (React Native).

## Notes
Frontend communicates with API via CORS-enabled JSON endpoints.
