# Phase 12 — Automation: Prefect Orchestration & Task Flows

## Objective
Automate end-to-end collection, cleaning, indexing, and alerting pipeline execution using Prefect 3 flows.

## Alignment with problem statement & feasibility
Fulfills continuous, autonomous operational requirements.

## Prerequisites
Phase 11 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Prefect | 3.0.0 | Pipeline orchestration |

## Repo layout after this phase
```
prometheus/orchestration/
├── __init__.py
├── tasks.py
└── flows.py
```

## Implementation Steps
### Step 1: Prefect Flow in `prometheus/orchestration/flows.py`
```python
from prefect import flow, task

@task
def run_scrape():
    return "scraped"

@task
def run_index(status: str):
    return "indexed"

@flow(name="prometheus-daily-pipeline")
def daily_pipeline():
    s = run_scrape()
    run_index(s)
```

## Deliverables
- `prometheus/orchestration/flows.py`
- `prometheus/orchestration/tasks.py`
- `tests/unit/test_flows.py`

## Definition of Done
```bash
pytest tests/unit/test_flows.py
```

## Out of Scope
Apache Airflow migration.

## Notes
Runs automatically every 6 hours.
