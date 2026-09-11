import os

PHASES = [
    {
        "num": "00",
        "name": "foundation",
        "title": "Phase 00 — Foundation: Repo, Environments & Base Scaffolding",
        "objective": "Establish the complete project directory layout, Python package environment, settings configuration, Makefile automation, and progress tracking framework.",
        "alignment": "Directly supports SIH26056 by establishing a reproducible, production-ready engineering foundation.",
        "prereqs": "Python 3.12+, Git.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Python | 3.12 | Core runtime |\n| Pydantic Settings | 2.3.0 | Environment configuration |\n| Typer | 0.12.3 | CLI application framework |",
        "layout": "```\nAirfare-index/\n├── prometheus/\n│   ├── __init__.py\n│   ├── config.py\n│   └── cli.py\n├── .env.example\n├── pyproject.toml\n├── Makefile\n└── PROGRESS.md\n```",
        "steps": """### Step 1: Create Pydantic Settings in `prometheus/config.py`
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
```""",
        "deliverables": "- `pyproject.toml`\n- `.env.example`\n- `prometheus/config.py`\n- `prometheus/cli.py`\n- `Makefile`\n- `PROGRESS.md`",
        "dod": "```bash\npython -m prometheus.cli info\npytest tests/\n```",
        "out_of_scope": "Scraping logic, database connection setup, frontend layout.",
        "notes": "Ensure python-dotenv is installed."
    },
    {
        "num": "01",
        "name": "data-model",
        "title": "Phase 01 — Data Model: Canonical FareObservation Schema & Pydantic Contracts",
        "objective": "Define the strict data contracts and validation rules governing every airfare observation captured across all airlines and OTAs.",
        "alignment": "Ensures standardized data capture across diverse source APIs and web DOM structures.",
        "prereqs": "Phase 00 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Pydantic | 2.7.1 | Data validation & schemas |",
        "layout": "```\nprometheus/models/\n├── __init__.py\n├── fare.py\n├── index.py\n└── alert.py\n```",
        "steps": """### Step 1: Create `prometheus/models/fare.py`
```python
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class SourceType(str, Enum):
    AIRLINE_DIRECT = "AIRLINE_DIRECT"
    OTA = "OTA"

class CabinClass(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"

class FareObservation(BaseModel):
    scraped_at: datetime
    source_type: SourceType
    source_name: str
    carrier_iata: str = Field(min_length=2, max_length=2)
    flight_number: str
    origin_iata: str = Field(min_length=3, max_length=3)
    destination_iata: str = Field(min_length=3, max_length=3)
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    duration_minutes: int
    stops: int = 0
    cabin_class: CabinClass = CabinClass.ECONOMY
    base_fare_inr: Decimal
    taxes_inr: Decimal
    total_fare_inr: Decimal
    seats_available: Optional[int] = None
    raw_hash: str

    @field_validator("origin_iata", "destination_iata")
    def upper_iata(cls, v: str) -> str:
        return v.upper()
```""",
        "deliverables": "- `prometheus/models/fare.py`\n- `prometheus/models/index.py`\n- `prometheus/models/alert.py`\n- `tests/unit/test_models.py`",
        "dod": "```bash\npytest tests/unit/test_models.py\n```",
        "out_of_scope": "Database tables and ORM mappings (handled in Phase 05).",
        "notes": "Fares must always be denominated in INR."
    },
    {
        "num": "02",
        "name": "scraping",
        "title": "Phase 02 — Scraping: Framework + Airline & OTA Scrapers",
        "objective": "Build the asynchronous web scraping framework using Playwright to ingest flight data from IndiGo, MakeMyTrip, and Air India.",
        "alignment": "Fulfills real-time data collection requirement across domestic airlines and OTAs.",
        "prereqs": "Phase 01 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Playwright | 1.44.0 | Browser automation |\n| Tenacity | 8.2.3 | Retry mechanisms |",
        "layout": "```\nprometheus/scrapers/\n├── __init__.py\n├── base.py\n├── airlines/\n│   ├── indigo.py\n│   └── airindia.py\n└── ota/\n    └── makemytrip.py\n```",
        "steps": """### Step 1: Base Scraper Class `prometheus/scrapers/base.py`
```python
from abc import ABC, abstractmethod
from typing import List
from prometheus.models.fare import FareObservation
from playwright.async_api import async_playwright
import structlog

logger = structlog.get_logger()

class BaseScraper(ABC):
    def __init__(self, headless: bool = True):
        self.headless = headless

    @abstractmethod
    async def scrape_route(self, origin: str, destination: str, travel_date: str) -> List[FareObservation]:
        pass
```""",
        "deliverables": "- `prometheus/scrapers/base.py`\n- `prometheus/scrapers/airlines/indigo.py`\n- `prometheus/scrapers/ota/makemytrip.py`\n- `tests/unit/test_scrapers.py`",
        "dod": "```bash\npytest tests/unit/test_scrapers.py\n```",
        "out_of_scope": "Captcha breaking services or residential proxy network integration.",
        "notes": "Always emulate standard desktop user agents."
    },
    {
        "num": "03",
        "name": "raw-storage",
        "title": "Phase 03 — Raw Storage: MinIO Object Store & Parquet Lake",
        "objective": "Implement raw object storage for HTML/JSON payloads in MinIO and compressed Parquet files for long-term analytical storage.",
        "alignment": "Provides data lineage auditability and high-performance analytical storage.",
        "prereqs": "Phase 02 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| MinIO Client | 7.2.7 | S3 compatible storage |\n| PyArrow | 16.1.0 | Parquet conversion |",
        "layout": "```\nprometheus/storage/\n├── __init__.py\n├── minio_client.py\n└── parquet_writer.py\n```",
        "steps": """### Step 1: MinIO Client in `prometheus/storage/minio_client.py`
```python
from minio import Minio
from prometheus.config import settings
import io

class StorageManager:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )

    def save_raw(self, bucket: str, object_name: str, content: bytes):
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
        self.client.put_object(bucket, object_name, io.BytesIO(content), len(content))
```""",
        "deliverables": "- `prometheus/storage/minio_client.py`\n- `prometheus/storage/parquet_writer.py`\n- `tests/unit/test_storage.py`",
        "dod": "```bash\npytest tests/unit/test_storage.py\n```",
        "out_of_scope": "AWS S3 multi-region replication.",
        "notes": "Partition parquet files by year/month/day/route."
    },
    {
        "num": "04",
        "name": "etl",
        "title": "Phase 04 — ETL: Data Cleaning, Normalisation & Quality Gates",
        "objective": "Process raw observations through strict cleaning rules, standardisation, deduplication, and automated quality metrics.",
        "alignment": "Guarantees index integrity by filtering out invalid or incomplete fare records.",
        "prereqs": "Phase 03 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Pandas | 2.2.2 | In-memory data transformation |",
        "layout": "```\nprometheus/etl/\n├── __init__.py\n├── cleaning.py\n├── normalisation.py\n├── deduplication.py\n└── quality.py\n```",
        "steps": """### Step 1: Quality Gate in `prometheus/etl/quality.py`
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
```""",
        "deliverables": "- `prometheus/etl/cleaning.py`\n- `prometheus/etl/deduplication.py`\n- `prometheus/etl/quality.py`\n- `tests/unit/test_etl.py`",
        "dod": "```bash\npytest tests/unit/test_etl.py\n```",
        "out_of_scope": "Real-time streaming ETL (Kafka/Flink). Batch processing is sufficient.",
        "notes": "Observations older than 24h are discarded during realtime pipeline runs."
    },
    {
        "num": "05",
        "name": "database",
        "title": "Phase 05 — Database: PostgreSQL Schema & Access Layer",
        "objective": "Define SQLAlchemy 2.0 ORM models, repository patterns, and Alembic database migrations.",
        "alignment": "Provides reliable, relational OLTP storage for index values, alerts, and fare history.",
        "prereqs": "Phase 04 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| SQLAlchemy | 2.0.30 | Async ORM |\n| Alembic | 1.13.1 | Schema migrations |",
        "layout": "```\nprometheus/db/\n├── __init__.py\n├── models.py\n├── session.py\n└── repository.py\n```",
        "steps": """### Step 1: ORM Models in `prometheus/db/models.py`
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Numeric, DateTime, Integer
from datetime import datetime

class Base(DeclarativeBase):
    pass

class FareObservationORM(Base):
    __tablename__ = "fare_observations"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    carrier_iata: Mapped[str] = mapped_column(String(2), index=True)
    origin_iata: Mapped[str] = mapped_column(String(3), index=True)
    destination_iata: Mapped[str] = mapped_column(String(3), index=True)
    total_fare_inr: Mapped[float] = mapped_column(Numeric(10, 2))
    raw_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
```""",
        "deliverables": "- `prometheus/db/models.py`\n- `prometheus/db/session.py`\n- `prometheus/db/repository.py`\n- `alembic/versions/`\n- `tests/unit/test_repository.py`",
        "dod": "```bash\npytest tests/unit/test_repository.py\n```",
        "out_of_scope": "Multi-master database clustering.",
        "notes": "Always use asyncpg database driver."
    },
    {
        "num": "06",
        "name": "index-engine",
        "title": "Phase 06 — Index Engine: Jevons Route Index & Aggregate APIx",
        "objective": "Implement the core mathematical formula (Jevons geometric mean) and national passenger-weighted APIx aggregation.",
        "alignment": "Core mathematical mandate of SIH26056 to deliver the Airfare Price Index.",
        "prereqs": "Phase 05 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| NumPy | 1.26.4 | Vectorised geometric mean math |",
        "layout": "```\nprometheus/index/\n├── __init__.py\n├── jevons.py\n├── weighting.py\n└── aggregation.py\n```",
        "steps": """### Step 1: Jevons Index Calculation `prometheus/index/jevons.py`
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
```""",
        "deliverables": "- `prometheus/index/jevons.py`\n- `prometheus/index/weighting.py`\n- `prometheus/index/aggregation.py`\n- `tests/unit/test_index.py`",
        "dod": "```bash\npytest tests/unit/test_index.py\n```",
        "out_of_scope": "Hedonic quality adjustment regression models.",
        "notes": "Route weights sum strictly to 1.0."
    },
    {
        "num": "07",
        "name": "dashboard",
        "title": "Phase 07 — Dashboard: FastAPI Web API & Next.js UI (MVP)",
        "objective": "Build the user presentation layer consisting of REST endpoints and an interactive React dashboard for visualization.",
        "alignment": "Delivers the MVP product interface for stakeholders and evaluation judges.",
        "prereqs": "Phase 06 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| FastAPI | 0.111.0 | RESTful API engine |\n| Next.js | 14.0 | Interactive React frontend |",
        "layout": "```\nprometheus/api/\n├── __init__.py\n├── main.py\n└── routers/\nfrontend/\n├── app/\n└── package.json\n```",
        "steps": """### Step 1: FastAPI App in `prometheus/api/main.py`
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
```""",
        "deliverables": "- `prometheus/api/main.py`\n- `prometheus/api/routers/index.py`\n- `frontend/app/page.tsx`\n- `tests/unit/test_api.py`",
        "dod": "```bash\npytest tests/unit/test_api.py\n```",
        "out_of_scope": "Mobile application (React Native).",
        "notes": "Frontend communicates with API via CORS-enabled JSON endpoints."
    },
    {
        "num": "08",
        "name": "basic-alerts",
        "title": "Phase 08 — Basic Alerts: Rule-Based WoW % Change & Z-Score Alerts",
        "objective": "Implement automated detection rules triggering notifications for extreme week-over-week fare spikes or statistical anomalies.",
        "alignment": "Provides proactive notification mechanisms for inflation monitor officers.",
        "prereqs": "Phase 07 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Redis | 7.0 | Pub/Sub messaging engine |",
        "layout": "```\nprometheus/alerts/\n├── __init__.py\n├── rules.py\n└── engine.py\n```",
        "steps": """### Step 1: Alert Rules in `prometheus/alerts/rules.py`
```python
class AlertRuleEngine:
    @staticmethod
    def check_wow_change(current_index: float, previous_week_index: float, threshold_pct: float = 15.0) -> bool:
        if previous_week_index == 0:
            return False
        pct_change = abs((current_index - previous_week_index) / previous_week_index) * 100.0
        return pct_change >= threshold_pct
```""",
        "deliverables": "- `prometheus/alerts/rules.py`\n- `prometheus/alerts/engine.py`\n- `tests/unit/test_alerts.py`",
        "dod": "```bash\npytest tests/unit/test_alerts.py\n```",
        "out_of_scope": "SMS gateway integration (Twilio). Email/Redis is sufficient.",
        "notes": "Alerts are deduplicated over a 24-hour rolling window."
    },
    {
        "num": "09",
        "name": "ml-anomaly",
        "title": "Phase 09 — ML Anomaly: Isolation Forest Unsupervised Anomaly Detection",
        "objective": "Deploy machine learning anomaly detection to isolate irregular flight pricing patterns across lead times and routes.",
        "alignment": "Enhances analytical depth by differentiating true inflation from isolated carrier pricing anomalies.",
        "prereqs": "Phase 08 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Scikit-Learn | 1.5.0 | Isolation Forest algorithm |",
        "layout": "```\nprometheus/ml/\n├── __init__.py\n├── features.py\n└── anomaly.py\n```",
        "steps": """### Step 1: Anomaly Detector in `prometheus/ml/anomaly.py`
```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def train_and_predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        return self.model.fit_predict(feature_matrix)
```""",
        "deliverables": "- `prometheus/ml/features.py`\n- `prometheus/ml/anomaly.py`\n- `tests/unit/test_ml_anomaly.py`",
        "dod": "```bash\npytest tests/unit/test_ml_anomaly.py\n```",
        "out_of_scope": "Deep learning autoencoders.",
        "notes": "Retrain model weekly."
    },
    {
        "num": "10",
        "name": "forecasting",
        "title": "Phase 10 — Forecasting: Time-Series Baseline Forecasting",
        "objective": "Build predictive models forecasting short-term airfare index trends for 7 to 14 days ahead.",
        "alignment": "Delivers forward-looking inflation intelligence to policy analysts.",
        "prereqs": "Phase 09 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Statsmodels | 0.14.2 | SARIMA modeling |\n| Prophet | 1.1.5 | Seasonal decomposition |",
        "layout": "```\nprometheus/ml/forecasting.py\n```",
        "steps": """### Step 1: Forecaster in `prometheus/ml/forecasting.py`
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np

class IndexForecaster:
    @staticmethod
    def forecast_sarima(series: np.ndarray, steps: int = 7) -> np.ndarray:
        model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
        fit = model.fit(disp=False)
        return fit.forecast(steps=steps)
```""",
        "deliverables": "- `prometheus/ml/forecasting.py`\n- `tests/unit/test_forecasting.py`",
        "dod": "```bash\npytest tests/unit/test_forecasting.py\n```",
        "out_of_scope": "LSTM / Transformer neural forecasting.",
        "notes": "Includes 80% confidence interval boundaries."
    },
    {
        "num": "11",
        "name": "explainability",
        "title": "Phase 11 — Explainability: Route Contribution & Feature Importance",
        "objective": "Deconstruct index movements into exact contribution percentages per route, lead-time window, and carrier.",
        "alignment": "Provides transparent auditability so users understand *why* the index moved.",
        "prereqs": "Phase 10 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| NumPy | 1.26.4 | Mathematical decomposition |",
        "layout": "```\nprometheus/ml/explainability.py\n```",
        "steps": """### Step 1: Contribution Engine in `prometheus/ml/explainability.py`
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
```""",
        "deliverables": "- `prometheus/ml/explainability.py`\n- `tests/unit/test_explainability.py`",
        "dod": "```bash\npytest tests/unit/test_explainability.py\n```",
        "out_of_scope": "SHAP compute clusters.",
        "notes": "Contribution percentages sum strictly to 100%."
    },
    {
        "num": "12",
        "name": "automation",
        "title": "Phase 12 — Automation: Prefect Orchestration & Task Flows",
        "objective": "Automate end-to-end collection, cleaning, indexing, and alerting pipeline execution using Prefect 3 flows.",
        "alignment": "Fulfills continuous, autonomous operational requirements.",
        "prereqs": "Phase 11 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Prefect | 3.0.0 | Pipeline orchestration |",
        "layout": "```\nprometheus/orchestration/\n├── __init__.py\n├── tasks.py\n└── flows.py\n```",
        "steps": """### Step 1: Prefect Flow in `prometheus/orchestration/flows.py`
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
```""",
        "deliverables": "- `prometheus/orchestration/flows.py`\n- `prometheus/orchestration/tasks.py`\n- `tests/unit/test_flows.py`",
        "dod": "```bash\npytest tests/unit/test_flows.py\n```",
        "out_of_scope": "Apache Airflow migration.",
        "notes": "Runs automatically every 6 hours."
    },
    {
        "num": "13",
        "name": "docker",
        "title": "Phase 13 — Docker: Full Containerization & Docker Compose",
        "objective": "Package all microservices (API, worker, database, MinIO, Redis, frontend) into reproducible multi-stage Docker images.",
        "alignment": "Guarantees 100% reproducible execution across local and cloud environments.",
        "prereqs": "Phase 12 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Docker Compose | 2.27 | Container stack management |",
        "layout": "```\nDockerfile\ndocker-compose.yml\n.dockerignore\n```",
        "steps": """### Step 1: Master `docker-compose.yml`
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
```""",
        "deliverables": "- `Dockerfile`\n- `docker-compose.yml`\n- `.dockerignore`",
        "dod": "```bash\ndocker compose config\n```",
        "out_of_scope": "Kubernetes Helm charts.",
        "notes": "Uses health checks for container startup ordering."
    },
    {
        "num": "14",
        "name": "auth",
        "title": "Phase 14 — Auth: OAuth2 / OIDC & Role-Based Access Control (RBAC)",
        "objective": "Implement secure user authentication, JWT token handling, and role-based permissions across API routes.",
        "alignment": "Ensures enterprise-grade security for government administrative interfaces.",
        "prereqs": "Phase 13 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Python-Jose | 3.3.0 | JWT generation & verification |",
        "layout": "```\nprometheus/auth/\n├── __init__.py\n├── jwt.py\n└── rbac.py\n```",
        "steps": """### Step 1: JWT Handling in `prometheus/auth/jwt.py`
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET = "SECRET_KEY"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
```""",
        "deliverables": "- `prometheus/auth/jwt.py`\n- `prometheus/auth/rbac.py`\n- `tests/unit/test_auth.py`",
        "dod": "```bash\npytest tests/unit/test_auth.py\n```",
        "out_of_scope": "Hardware token / WebAuthn integration.",
        "notes": "Roles: ADMIN, ANALYST, VIEWER."
    },
    {
        "num": "15",
        "name": "production",
        "title": "Phase 15 — Production: CI/CD, Prometheus Monitoring & Cloud Deploy",
        "objective": "Establish automated CI/CD pipelines in GitHub Actions, Prometheus telemetry metrics, and cloud deployment guides.",
        "alignment": "Final production-readiness step for enterprise deployment.",
        "prereqs": "Phase 14 completed.",
        "tech": "| Tool | Version | Purpose |\n|---|---|---|\n| Prometheus Client | 0.20.0 | Operational metrics exporters |\n| GitHub Actions | v4 | Automated CI/CD runner |",
        "layout": "```\n.github/workflows/ci.yml\nprometheus/monitoring/\n├── __init__.py\n└── metrics.py\n```",
        "steps": """### Step 1: CI Pipeline in `.github/workflows/ci.yml`
```yaml
name: PROMETHEUS CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check prometheus tests
      - run: pytest tests/
```""",
        "deliverables": "- `.github/workflows/ci.yml`\n- `prometheus/monitoring/metrics.py`\n- `docs/deployment-guide.md`",
        "dod": "```bash\npytest tests/\n```",
        "out_of_scope": "Multi-region failover cluster orchestration.",
        "notes": "Metrics exported at /metrics endpoint."
    }
]

for p in PHASES:
    filename = f"docs/phases/phase-{p['num']}-{p['name']}.md"
    content = f"""# {p['title']}

## Objective
{p['objective']}

## Alignment with problem statement & feasibility
{p['alignment']}

## Prerequisites
{p['prereqs']}

## Tech choices (this phase)
{p['tech']}

## Repo layout after this phase
{p['layout']}

## Implementation Steps
{p['steps']}

## Deliverables
{p['deliverables']}

## Definition of Done
{p['dod']}

## Out of Scope
{p['out_of_scope']}

## Notes
{p['notes']}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {filename}")

print("All phase files created successfully.")
