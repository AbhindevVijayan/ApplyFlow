import pytest
from sqlalchemy import text

from packages.database.session import SessionFactory


@pytest.mark.asyncio
async def test_database_connection() -> None:
    async with SessionFactory() as session:
        result = await session.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
