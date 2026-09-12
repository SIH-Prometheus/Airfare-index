from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prometheus.config import settings

logger = structlog.get_logger(__name__)

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_async_engine() -> AsyncEngine:
    """
    Return the application's shared async SQLAlchemy engine.

    The engine uses PostgreSQL connection pooling for production
    workloads. It is created lazily on first use.
    """
    global _engine

    if _engine is None:
        _engine = create_async_engine(
            settings.DB_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            echo=False,
        )

    return _engine


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Return the shared async session factory.
    """
    global _session_maker

    if _session_maker is None:
        _session_maker = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    return _session_maker


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session with automatic commit/rollback handling.

    Successful operations are committed.
    Exceptions trigger a rollback and are re-raised.
    """
    session_maker = get_async_session_maker()

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_connection() -> bool:
    """
    Check whether PostgreSQL is reachable.
    """
    engine = get_async_engine()

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1

    except Exception as exc:
        logger.error(
            "Database connection check failed",
            error=str(exc),
        )
        return False


async def close_async_engine() -> None:
    """
    Dispose the async SQLAlchemy engine and clear global state.

    This is important during application shutdown and test teardown,
    especially because async SQLAlchemy connection pools must not be
    reused across different event loops.
    """
    global _engine, _session_maker

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_maker = None