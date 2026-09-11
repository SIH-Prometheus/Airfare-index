# Phase 00 — Foundation: Repo, Environments & Base Scaffolding

## Objective
Establish the complete project directory layout, Python package environment, settings configuration, Makefile automation, and progress tracking framework.

## Alignment with problem statement & feasibility
Directly supports SIH26056 by establishing a reproducible, production-ready engineering foundation.

## Prerequisites
Python 3.12+, Git.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Core runtime |
| Pydantic Settings | 2.3.0 | Environment configuration |
| Typer | 0.12.3 | CLI application framework |

## Repo layout after this phase
```
Airfare-index/
├── prometheus/
│   ├── __init__.py
│   ├── config.py
│   └── cli.py
├── .env.example
├── pyproject.toml
├── Makefile
└── PROGRESS.md
```

## Implementation Steps
### Step 1: Create Pydantic Settings in `prometheus/config.py`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROMETHEUS_", env_file=".env", extra="ignore")

    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    DB_URL: str = Field(default="postgresql+asyncpg://prometheus:secret@localhost:5432/prometheus")
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET_RAW: str = Field(default="prometheus-raw")
    MINIO_BUCKET_PARQUET: str = Field(default="prometheus-parquet")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    SECRET_KEY: str = Field(default="change-me-to-a-random-64-char-hex-string")

settings = Settings()
```

### Step 2: Create CLI Entry point in `prometheus/cli.py`
```python
import typer
from prometheus.config import settings

app = typer.Typer(help="PROMETHEUS Airfare Price Index CLI")

@app.command()
def info():
    typer.echo(f"PROMETHEUS Environment: {settings.ENV}")
    typer.echo(f"Log Level: {settings.LOG_LEVEL}")

if __name__ == "__main__":
    app()
```

## Deliverables
- `pyproject.toml`
- `.env.example`
- `prometheus/config.py`
- `prometheus/cli.py`
- `Makefile`
- `PROGRESS.md`

## Definition of Done
```bash
python -m prometheus.cli info
pytest tests/
```

## Out of Scope
Scraping logic, database connection setup, frontend layout.

## Notes
Ensure python-dotenv is installed.
