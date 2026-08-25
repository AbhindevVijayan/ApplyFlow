from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from packages.api.app import app
from packages.api.dependencies import get_discovery_use_case
from packages.application.discovery.run_discovery import DiscoveryResult
from packages.config.settings import Settings
from packages.database.session import get_session


@pytest.mark.asyncio
async def test_discovery_returns_disabled_when_greenhouse_is_disabled() -> None:
    session = AsyncMock()

    async def override_get_session() -> AsyncIterator[AsyncMock]:
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        settings = Settings(
            greenhouse_enabled=False,
            greenhouse_board_tokens="acme",
        )

        with patch(
            "packages.api.routes.discovery.get_settings",
            return_value=settings,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post("/discovery/run")

        assert response.status_code == 200

        assert response.json() == {
            "status": "disabled",
            "sources": [],
            "jobs_discovered": 0,
        }

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_discovery_runs_when_greenhouse_is_enabled() -> None:
    use_case = AsyncMock()

    use_case.execute.return_value = [
        DiscoveryResult(
            source="greenhouse",
            status="completed",
            jobs=(),
            discovered_count=0,
            persisted_count=0,
            duplicate_count=0,
        ),
    ]

    async def override_discovery_use_case() -> AsyncIterator[AsyncMock]:
        yield use_case

    app.dependency_overrides[get_discovery_use_case] = override_discovery_use_case

    try:
        settings = Settings(
            greenhouse_enabled=True,
            greenhouse_board_tokens="acme",
        )

        with patch(
            "packages.api.routes.discovery.get_settings",
            return_value=settings,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post("/discovery/run")

        assert response.status_code == 200

        assert response.json() == {
            "status": "completed",
            "sources": [
                {
                    "source": "greenhouse",
                    "jobs_discovered": 0,
                },
            ],
            "jobs_discovered": 0,
        }

        use_case.execute.assert_awaited_once()

    finally:
        app.dependency_overrides.clear()
