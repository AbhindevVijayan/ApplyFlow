from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from packages.api.app import app
from packages.database.session import get_session


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    session = AsyncMock()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "ok"
        assert body["services"]["api"] == "ok"
        assert body["services"]["database"] == "ok"
    finally:
        app.dependency_overrides.clear()
