# =============================================================================
# PROMETHEUS — Makefile
# =============================================================================
.PHONY: install lint format test test-unit test-integration run-api docker-up docker-down migrate seed clean

PYTHON := python
UV     := uv
PKG    := prometheus

## ── Setup ────────────────────────────────────────────────────────────────────
install:
	$(UV) pip install -e ".[dev]"
	playwright install chromium

install-pip:
	pip install -e ".[dev]"
	playwright install chromium

## ── Code quality ─────────────────────────────────────────────────────────────
lint:
	ruff check $(PKG) tests
	black --check $(PKG) tests

format:
	ruff check --fix $(PKG) tests
	black $(PKG) tests

typecheck:
	mypy $(PKG)

## ── Tests ────────────────────────────────────────────────────────────────────
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m integration

test-e2e:
	pytest tests/e2e/ -v -m e2e

## ── API ──────────────────────────────────────────────────────────────────────
run-api:
	uvicorn prometheus.api.main:app --host 0.0.0.0 --port 8000 --reload

## ── Database ─────────────────────────────────────────────────────────────────
migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-gen:
	alembic revision --autogenerate -m "$(MSG)"

## ── Docker ───────────────────────────────────────────────────────────────────
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-build:
	docker compose build

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

## ── Seed / demo data ─────────────────────────────────────────────────────────
seed:
	$(PYTHON) scripts/seed_data.py

## ── Scraper ──────────────────────────────────────────────────────────────────
scrape-once:
	$(PYTHON) -m prometheus.cli scrape --routes DEL-BOM,BOM-BLR --days 7

## ── Clean ────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info

## ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "PROMETHEUS make targets:"
	@echo "  install          Install all dependencies (uv)"
	@echo "  install-pip      Install all dependencies (pip)"
	@echo "  lint             Run ruff + black check"
	@echo "  format           Auto-fix with ruff + black"
	@echo "  test             Run full test suite"
	@echo "  test-unit        Unit tests only"
	@echo "  test-integration Integration tests (require services)"
	@echo "  run-api          Start FastAPI dev server on :8000"
	@echo "  docker-up        Start all services via docker compose"
	@echo "  docker-down      Stop all services"
	@echo "  migrate          Apply database migrations"
	@echo "  seed             Seed synthetic demo data"
