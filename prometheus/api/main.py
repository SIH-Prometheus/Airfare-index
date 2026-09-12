"""
prometheus/api/main.py — FastAPI application entry-point.

MVP Phase: DEL→BOM Airfare Price Index (APIx)
Run:
    uvicorn prometheus.api.main:app --reload --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from prometheus.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=settings.LOG_LEVEL)


# ── Database schema auto-init ─────────────────────────────────────────────────

async def _init_db() -> None:
    """Create all MVP tables if they don't exist yet. Retried on first request if startup fails."""
    from prometheus.database.models import Base
    from prometheus.database.session import get_async_engine

    engine = get_async_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialised (create_all OK)")
    except Exception as exc:
        # Non-fatal at startup — DB might not be ready yet; session will retry
        logger.warning("DB schema init failed at startup (will retry on first request): %s", exc)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("PROMETHEUS starting — env: %s", settings.ENV)
    await _init_db()
    yield
    from prometheus.database.session import close_async_engine
    await close_async_engine()
    logger.info("PROMETHEUS stopped cleanly")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PROMETHEUS — Airfare Price Index API",
    description=(
        "Real-time APIx for India | SIH26056\n\n"
        "**MVP scope**: DEL → BOM route  \n"
        "**ML/Forecasting**: excluded from MVP — Phase 2 extension point."
    ),
    version="1.0.0-mvp",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────

origins = settings.cors_origins_list
logger.info("CORS allowed origins: %s", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── MVP Router (primary — wired to real DB + MinIO) ───────────────────────────

from prometheus.api.routers import mvp as mvp_router
app.include_router(mvp_router.router)


# ── Legacy seed-data routers (backward-compat, return mock data) ──────────────
# These are wrapped in try/except so a broken dependency in one router
# does NOT prevent the MVP from starting.

def _safe_include(module_path: str, attr: str = "router") -> None:
    try:
        import importlib
        mod = importlib.import_module(module_path)
        app.include_router(getattr(mod, attr))
        logger.debug("Included legacy router: %s", module_path)
    except Exception as exc:
        logger.warning("Legacy router %s skipped (non-critical): %s", module_path, exc)


_safe_include("prometheus.api.routers.index")
_safe_include("prometheus.api.routers.fares")
_safe_include("prometheus.api.routers.routes")
_safe_include("prometheus.api.routers.alerts")
_safe_include("prometheus.api.routers.metadata")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health() -> dict:
    """
    Health check. Reports PostgreSQL and MinIO connectivity.
    Returns HTTP 200 regardless of dependency state (for Docker health checks).
    """
    from prometheus.database.session import check_db_connection
    from prometheus.storage.minio_client import get_minio_client

    db_ok = False
    minio_ok = False

    try:
        db_ok = await check_db_connection()
    except Exception as exc:
        logger.warning("Health: DB check failed: %s", exc)

    try:
        minio_ok = get_minio_client().check_connection()
    except Exception as exc:
        logger.warning("Health: MinIO check failed: %s", exc)

    overall = "ok" if (db_ok and minio_ok) else "degraded"
    return {
        "status": overall,
        "phase": "07",
        "service": "prometheus-api",
        "version": "1.0.0-mvp",
        "dependencies": {
            "postgresql": "ok" if db_ok else "unavailable",
            "minio": "ok" if minio_ok else "unavailable",
        },
    }


# ── Global exception handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):  # type: ignore[no-untyped-def]
    logger.error("Unhandled exception on %s: %s", request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": "An unexpected error occurred"},
    )


# ── Dev runner ────────────────────────────────────────────────────────────────

def start() -> None:
    import uvicorn
    uvicorn.run("prometheus.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
