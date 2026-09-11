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

settings = Settings()
