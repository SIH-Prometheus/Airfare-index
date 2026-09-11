# Phase 08 — Basic Alerts: Rule-Based WoW % Change & Z-Score Alerts

## Objective
Implement automated detection rules triggering notifications for extreme week-over-week fare spikes or statistical anomalies.

## Alignment with problem statement & feasibility
Provides proactive notification mechanisms for inflation monitor officers.

## Prerequisites
Phase 07 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Redis | 7.0 | Pub/Sub messaging engine |

## Repo layout after this phase
```
prometheus/alerts/
├── __init__.py
├── rules.py
└── engine.py
```

## Implementation Steps
### Step 1: Alert Rules in `prometheus/alerts/rules.py`
```python
class AlertRuleEngine:
    @staticmethod
    def check_wow_change(current_index: float, previous_week_index: float, threshold_pct: float = 15.0) -> bool:
        if previous_week_index == 0:
            return False
        pct_change = abs((current_index - previous_week_index) / previous_week_index) * 100.0
        return pct_change >= threshold_pct
```

## Deliverables
- `prometheus/alerts/rules.py`
- `prometheus/alerts/engine.py`
- `tests/unit/test_alerts.py`

## Definition of Done
```bash
pytest tests/unit/test_alerts.py
```

## Out of Scope
SMS gateway integration (Twilio). Email/Redis is sufficient.

## Notes
Alerts are deduplicated over a 24-hour rolling window.
