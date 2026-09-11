# Phase 13 — Docker: Full Containerization & Docker Compose

## Objective
Package all microservices (API, worker, database, MinIO, Redis, frontend) into reproducible multi-stage Docker images.

## Alignment with problem statement & feasibility
Guarantees 100% reproducible execution across local and cloud environments.

## Prerequisites
Phase 12 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Docker Compose | 2.27 | Container stack management |

## Repo layout after this phase
```
Dockerfile
docker-compose.yml
.dockerignore
```

## Implementation Steps
### Step 1: Master `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: prometheus
      POSTGRES_USER: prometheus
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"

  minio:
    image: minio/minio:RELEASE.2024-05-28T17-19-04Z
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Deliverables
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

## Definition of Done
```bash
docker compose config
```

## Out of Scope
Kubernetes Helm charts.

## Notes
Uses health checks for container startup ordering.
