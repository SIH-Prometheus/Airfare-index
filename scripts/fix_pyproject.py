content = """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "prometheus-apix"
version = "0.1.0"
description = "Real-time Airfare Price Index (APIx) for India — SIH26056"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.12"
authors = [{ name = "SIH26056 Team" }]

dependencies = [
    "playwright==1.44.0",
    "httpx==0.27.0",
    "tenacity==8.2.3",
    "pydantic==2.7.1",
    "pydantic-settings==2.3.0",
    "fastapi==0.111.0",
    "sqlalchemy==2.0.30",
    "alembic==1.13.1",
    "pyarrow==16.1.0",
    "redis==5.0.4",
    "structlog==24.2.0",
    "python-dotenv==1.0.1",
    "typer==0.12.3",
    "rich==13.7.1"
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
"""
with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(content)
print("pyproject.toml written clean.")
