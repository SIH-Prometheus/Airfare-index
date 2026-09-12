from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROMETHEUS_", env_file=".env", extra="ignore")

    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    DB_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/prometheus")
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)
    DB_POOL_TIMEOUT: int = Field(default=30)
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET_RAW: str = Field(default="prometheus-raw")
    MINIO_BUCKET_PARQUET: str = Field(default="prometheus-parquet")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    SECRET_KEY: str = Field(default="change-me-to-a-random-64-char-hex-string")

settings = Settings()
