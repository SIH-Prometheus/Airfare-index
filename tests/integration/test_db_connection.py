import pytest
from prometheus.db.session import check_db_connection, get_db_session

@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_connection():
    connected = await check_db_connection()
    if not connected:
        pytest.skip("PostgreSQL database is not reachable at configured PROMETHEUS_DB_URL")
    assert connected is True

@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_session_query():
    connected = await check_db_connection()
    if not connected:
        pytest.skip("PostgreSQL database is not reachable at configured PROMETHEUS_DB_URL")
    
    from sqlalchemy import text
    async with get_db_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
