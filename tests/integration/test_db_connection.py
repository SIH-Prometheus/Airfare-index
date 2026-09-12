import pytest
import pytest_asyncio
from sqlalchemy import text

from prometheus.db.session import (
    check_db_connection,
    close_async_engine,
    get_db_session,
)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    """
    Dispose the async SQLAlchemy engine after every test.

    This prevents pooled connections from being reused across
    different pytest event loops.
    """
    yield
    await close_async_engine()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_connection():
    """Verify that PostgreSQL is reachable."""
    connected = await check_db_connection()

    assert connected is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_session_query():
    """Verify that an application database session can execute a query."""
    connected = await check_db_connection()

    assert connected is True

    async with get_db_session() as session:
        result = await session.execute(text("SELECT 1"))

        assert result.scalar() == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repeated_database_connectivity():
    """
    Verify that the same async engine can perform repeated database
    operations within the same event loop.
    """
    connected1 = await check_db_connection()
    connected2 = await check_db_connection()

    assert connected1 is True
    assert connected2 is True