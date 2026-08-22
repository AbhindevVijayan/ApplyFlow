from typing import Any

import httpx


class GreenhouseClientError(Exception):
    """Raised when the Greenhouse API cannot be accessed successfully."""


class GreenhouseClient:
    """HTTP client for the public Greenhouse Job Board API."""

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(
        self,
        board_token: str,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not board_token.strip():
            raise ValueError("Greenhouse board token cannot be empty.")

        self._board_token = board_token
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "GreenhouseClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
            )

        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def list_jobs(self) -> list[dict[str, Any]]:
        """Retrieve published jobs from a Greenhouse board."""

        if self._client is None:
            raise RuntimeError(
                "GreenhouseClient must be used as an async context manager "
                "when no HTTP client is supplied."
            )

        url = f"{self.BASE_URL}/{self._board_token}/jobs"

        try:
            response = await self._client.get(
                url,
                params={"content": "true"},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GreenhouseClientError(
                f"Failed to retrieve jobs from Greenhouse board '{self._board_token}'."
            ) from exc

        payload = response.json()

        jobs = payload.get("jobs")

        if not isinstance(jobs, list):
            raise GreenhouseClientError("Greenhouse API returned an invalid jobs payload.")

        return jobs
