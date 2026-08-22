from unittest.mock import AsyncMock

import pytest

from packages.infrastructure.discovery.greenhouse.client import (
    GreenhouseClient,
)
from packages.infrastructure.discovery.greenhouse.source import (
    GreenhouseJobSource,
)


@pytest.mark.asyncio
async def test_source_name_is_greenhouse() -> None:
    client = AsyncMock(spec=GreenhouseClient)

    source = GreenhouseJobSource(client)

    assert source.name == "greenhouse"


@pytest.mark.asyncio
async def test_discover_maps_greenhouse_jobs() -> None:
    client = AsyncMock(spec=GreenhouseClient)

    client.list_jobs.return_value = [
        {
            "company_name": "Acme",
            "title": "Python Engineer",
            "absolute_url": "https://example.com/jobs/1",
        },
        {
            "company_name": "Acme",
            "title": "Backend Engineer",
            "absolute_url": "https://example.com/jobs/2",
        },
    ]

    source = GreenhouseJobSource(client)

    jobs = await source.discover()

    assert len(jobs) == 2

    assert jobs[0].company == "Acme"
    assert jobs[0].title == "Python Engineer"
    assert jobs[0].source == "greenhouse"

    assert jobs[1].title == "Backend Engineer"

    client.list_jobs.assert_awaited_once()


@pytest.mark.asyncio
async def test_discover_skips_invalid_jobs() -> None:
    client = AsyncMock(spec=GreenhouseClient)

    client.list_jobs.return_value = [
        {
            "company_name": "Acme",
            "title": "Valid Engineer",
            "absolute_url": "https://example.com/jobs/1",
        },
        {
            "company_name": "Acme",
            "absolute_url": "https://example.com/jobs/2",
        },
        {
            "company_name": "Acme",
            "title": "Another Valid Job",
            "absolute_url": "https://example.com/jobs/3",
        },
    ]

    source = GreenhouseJobSource(client)

    jobs = await source.discover()

    assert len(jobs) == 2
    assert jobs[0].title == "Valid Engineer"
    assert jobs[1].title == "Another Valid Job"


@pytest.mark.asyncio
async def test_discover_returns_empty_sequence_when_no_jobs_exist() -> None:
    client = AsyncMock(spec=GreenhouseClient)
    client.list_jobs.return_value = []

    source = GreenhouseJobSource(client)

    jobs = await source.discover()

    assert jobs == []
    client.list_jobs.assert_awaited_once()
