import os

files = [
    "prometheus/__init__.py",
    "prometheus/config.py",
    "prometheus/cli.py",
    "prometheus/models/__init__.py",
    "prometheus/models/fare.py",
    "prometheus/models/index.py",
    "prometheus/models/alert.py",
    "prometheus/scrapers/__init__.py",
    "prometheus/scrapers/base.py",
    "prometheus/scrapers/airlines/__init__.py",
    "prometheus/scrapers/ota/__init__.py",
    "prometheus/storage/__init__.py",
    "prometheus/etl/__init__.py",
    "prometheus/db/__init__.py",
    "prometheus/index/__init__.py",
    "prometheus/api/__init__.py",
    "prometheus/alerts/__init__.py",
    "prometheus/ml/__init__.py",
    "prometheus/orchestration/__init__.py",
    "prometheus/auth/__init__.py",
    "prometheus/monitoring/__init__.py",
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/unit/__init__.py",
    "tests/unit/test_config.py",
]

for filepath in files:
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            if filepath.endswith("__init__.py"):
                f.write('"""PROMETHEUS package module."""\n')
            elif filepath == "prometheus/config.py":
                f.write('''from pydantic_settings import BaseSettings, SettingsConfigDict
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
''')
            elif filepath == "tests/unit/test_config.py":
                f.write('''from prometheus.config import settings

def test_config_defaults():
    assert settings.ENV in ["development", "staging", "production"]
    assert settings.LOG_LEVEL is not None
''')
            else:
                f.write('# Stub file for PROMETHEUS package\n')

print("Package scaffold updated.")
