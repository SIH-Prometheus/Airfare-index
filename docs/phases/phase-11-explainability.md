# Phase 11 — Explainability: Route Contribution & Feature Importance

## Objective
Deconstruct index movements into exact contribution percentages per route, lead-time window, and carrier.

## Alignment with problem statement & feasibility
Provides transparent auditability so users understand *why* the index moved.

## Prerequisites
Phase 10 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| NumPy | 1.26.4 | Mathematical decomposition |

## Repo layout after this phase
```
prometheus/ml/explainability.py
```

## Implementation Steps
### Step 1: Contribution Engine in `prometheus/ml/explainability.py`
```python
from typing import Dict

class ContributionEngine:
    @staticmethod
    def calculate_contributions(route_indices_t0: Dict[str, float], route_indices_t1: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
        contributions = {}
        total_change = sum((route_indices_t1[r] - route_indices_t0[r]) * weights[r] for r in weights)
        if total_change == 0:
            return {r: 0.0 for r in weights}
        
        for r in weights:
            change = (route_indices_t1[r] - route_indices_t0[r]) * weights[r]
            contributions[r] = (change / total_change) * 100.0
        return contributions
```

## Deliverables
- `prometheus/ml/explainability.py`
- `tests/unit/test_explainability.py`

## Definition of Done
```bash
pytest tests/unit/test_explainability.py
```

## Out of Scope
SHAP compute clusters.

## Notes
Contribution percentages sum strictly to 100%.
