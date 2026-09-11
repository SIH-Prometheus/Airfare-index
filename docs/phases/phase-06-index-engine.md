# Phase 06 — Index Engine: Jevons Route Index & Aggregate APIx

## Objective
Implement the core mathematical formula (Jevons geometric mean) and national passenger-weighted APIx aggregation.

## Alignment with problem statement & feasibility
Core mathematical mandate of SIH26056 to deliver the Airfare Price Index.

## Prerequisites
Phase 05 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| NumPy | 1.26.4 | Vectorised geometric mean math |

## Repo layout after this phase
```
prometheus/index/
├── __init__.py
├── jevons.py
├── weighting.py
└── aggregation.py
```

## Implementation Steps
### Step 1: Jevons Index Calculation `prometheus/index/jevons.py`
```python
import numpy as np
from typing import List

class JevonsIndexEngine:
    @staticmethod
    def calculate_route_index(current_fares: List[float], base_fares: List[float]) -> float:
        if not current_fares or not base_fares or len(current_fares) != len(base_fares):
            raise ValueError("Fare lists must be non-empty and equal in length")
        
        relatives = np.array(current_fares) / np.array(base_fares)
        return float(np.exp(np.mean(np.log(relatives)))) * 100.0
```

## Deliverables
- `prometheus/index/jevons.py`
- `prometheus/index/weighting.py`
- `prometheus/index/aggregation.py`
- `tests/unit/test_index.py`

## Definition of Done
```bash
pytest tests/unit/test_index.py
```

## Out of Scope
Hedonic quality adjustment regression models.

## Notes
Route weights sum strictly to 1.0.
