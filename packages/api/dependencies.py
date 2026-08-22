from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.discovery.run_discovery import RunDiscovery
from packages.config.settings import get_settings
from packages.database.repositories.job_adapter import JobRepositoryAdapter
from packages.database.session import get_session
from packages.infrastructure.discovery.greenhouse.client import GreenhouseClient
from packages.infrastructure.discovery.greenhouse.source import GreenhouseJobSource

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


async def get_discovery_use_case(
    session: SessionDependency,
) -> AsyncIterator[RunDiscovery]:
    """Build the job discovery use case for the current request."""

    settings = get_settings()

    repository = JobRepositoryAdapter(session)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0),
    ) as http_client:
        sources = [
            GreenhouseJobSource(
                GreenhouseClient(
                    board_token,
                    client=http_client,
                ),
            )
            for board_token in settings.greenhouse_boards()
        ]

        yield RunDiscovery(
            sources=sources,
            repository=repository,
        )
