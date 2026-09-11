# Phase 14 — Auth: OAuth2 / OIDC & Role-Based Access Control (RBAC)

## Objective
Implement secure user authentication, JWT token handling, and role-based permissions across API routes.

## Alignment with problem statement & feasibility
Ensures enterprise-grade security for government administrative interfaces.

## Prerequisites
Phase 13 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Python-Jose | 3.3.0 | JWT generation & verification |

## Repo layout after this phase
```
prometheus/auth/
├── __init__.py
├── jwt.py
└── rbac.py
```

## Implementation Steps
### Step 1: JWT Handling in `prometheus/auth/jwt.py`
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET = "SECRET_KEY"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
```

## Deliverables
- `prometheus/auth/jwt.py`
- `prometheus/auth/rbac.py`
- `tests/unit/test_auth.py`

## Definition of Done
```bash
pytest tests/unit/test_auth.py
```

## Out of Scope
Hardware token / WebAuthn integration.

## Notes
Roles: ADMIN, ANALYST, VIEWER.
