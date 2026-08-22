import httpx
import pytest

from packages.infrastructure.discovery.greenhouse.client import (
    GreenhouseClient,
    GreenhouseClientError,
)


@pytest.mark.asyncio
async def test_list_jobs_requests_greenhouse_jobs_with_content_enabled() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)

        return httpx.Response(
            status_code=200,
            json={
                "jobs": [
                    {
                        "id": 123,
                        "title": "Software Engineer",
                    },
                ],
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as http_client:
        async with GreenhouseClient(
            "acme",
            client=http_client,
        ) as greenhouse:
            jobs = await greenhouse.list_jobs()

    assert jobs == [
        {
            "id": 123,
            "title": "Software Engineer",
        },
    ]

    assert len(requests) == 1

    request = requests[0]

    assert request.method == "GET"
    assert str(request.url) == ("https://boards-api.greenhouse.io/v1/boards/acme/jobs?content=true")


@pytest.mark.asyncio
async def test_list_jobs_raises_for_http_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            json={"error": "Board not found"},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as http_client:
        async with GreenhouseClient(
            "invalid-board",
            client=http_client,
        ) as greenhouse:
            with pytest.raises(GreenhouseClientError):
                await greenhouse.list_jobs()


@pytest.mark.asyncio
async def test_list_jobs_rejects_invalid_jobs_payload() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "jobs": "not-a-list",
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as http_client:
        async with GreenhouseClient(
            "acme",
            client=http_client,
        ) as greenhouse:
            with pytest.raises(GreenhouseClientError):
                await greenhouse.list_jobs()


def test_empty_board_token_is_rejected() -> None:
    with pytest.raises(ValueError):
        GreenhouseClient("   ")


@pytest.mark.asyncio
async def test_list_jobs_requires_context_manager_without_injected_client() -> None:
    greenhouse = GreenhouseClient("acme")

    with pytest.raises(RuntimeError):
        await greenhouse.list_jobs()
