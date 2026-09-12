"""
prometheus/config.py — Centralised settings via pydantic-settings.
All values are injected via environment variables (PROMETHEUS_ prefix).
See .env.example for documentation of every variable.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PROMETHEUS_",
        env_file=".env",
        extra="ignore",
    )

    # ── Runtime ───────────────────────────────────────────────────────────────
    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    # Docker: postgresql+asyncpg://postgres:postgres@postgres:5432/airfare
    # Local:  postgresql+asyncpg://postgres:postgres@localhost:5432/airfare
    DB_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/airfare"
    )
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)
    DB_POOL_TIMEOUT: int = Field(default=30)

    # ── MinIO ─────────────────────────────────────────────────────────────────
    # Docker: minio:9000
    # Local:  localhost:9000
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET_RAW: str = Field(default="airfare-data")
    MINIO_SECURE: bool = Field(default=False)

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── Auth (keep for future phases) ─────────────────────────────────────────
    SECRET_KEY: str = Field(default="change-me-to-a-random-64-char-hex-string")

    # ── Redis (excluded from MVP, kept for Phase 2) ───────────────────────────
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # ── Scraper ───────────────────────────────────────────────────────────────
    SCRAPER_HEADLESS: bool = Field(default=True)
    SCRAPER_TIMEOUT_MS: int = Field(default=30000)

    # ── ML / Forecasting (EXCLUDED from MVP — extension point for Phase 2) ───
    # These settings are retained so existing ML code does not break at import.
    ML_CONTAMINATION: float = Field(default=0.05)
    FORECAST_HORIZON_DAYS: int = Field(default=14)


settings = Settings()
