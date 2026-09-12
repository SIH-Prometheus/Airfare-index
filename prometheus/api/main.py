"""
prometheus/api/main.py — FastAPI application entry-point for Phase 7.

Run:
    cd SIH
    uvicorn prometheus.api.main:app --reload --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from prometheus.api.routers import alerts, fares, index, metadata, routes


# ── Lifespan ─────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown hooks (add DB pool here in Phase 8)."""
    # Seed data is already initialised at module import time in seed.py
    yield


# ── App ──────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "PROMETHEUS — Airfare Price Index API",
    description = "Real-time APIx for India | SIH26056",
    version     = "0.7.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
    lifespan    = lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # Tighten in production / Phase 15
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────────

app.include_router(index.router)
app.include_router(fares.router)
app.include_router(routes.router)
app.include_router(alerts.router)
app.include_router(metadata.router)


# ── Health ────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok", "service": "prometheus-api", "phase": "07"}


# ── Global exception handler ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):  # type: ignore[no-untyped-def]
    return JSONResponse(
        status_code = 500,
        content     = {"error": "internal_server_error", "detail": str(exc)},
    )


# ── Dev runner ────────────────────────────────────────────────────────────────────

def start() -> None:
    import uvicorn
    uvicorn.run("prometheus.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
