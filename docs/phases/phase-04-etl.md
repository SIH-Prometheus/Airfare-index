# Phase 04 — ETL: Data Cleaning, Normalisation & Quality Gates

## Objective
Process raw observations through strict cleaning rules, standardisation, deduplication, and automated quality metrics.

## Alignment with problem statement & feasibility
Guarantees index integrity by filtering out invalid or incomplete fare records.

## Prerequisites
Phase 03 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Pandas | 2.2.2 | In-memory data transformation |

## Repo layout after this phase
```
prometheus/etl/
├── __init__.py
├── cleaning.py
├── normalisation.py
├── deduplication.py
└── quality.py
```

## Implementation Steps
### Step 1: Quality Gate in `prometheus/etl/quality.py`
```python
from typing import List, Tuple
from prometheus.models.fare import FareObservation

class QualityGate:
    @staticmethod
    def evaluate_batch(records: List[FareObservation]) -> Tuple[List[FareObservation], float]:
        if not records:
            return [], 0.0
        valid = [r for r in records if r.total_fare_inr > 500 and r.total_fare_inr < 200000]
        completeness_score = len(valid) / len(records)
        return valid, completeness_score
```

## Deliverables
- `prometheus/etl/cleaning.py`
- `prometheus/etl/deduplication.py`
- `prometheus/etl/quality.py`
- `tests/unit/test_etl.py`

## Definition of Done
```bash
pytest tests/unit/test_etl.py
```

## Out of Scope
Real-time streaming ETL (Kafka/Flink). Batch processing is sufficient.

## Notes
Observations older than 24h are discarded during realtime pipeline runs.
