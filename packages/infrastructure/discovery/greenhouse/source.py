from collections.abc import Sequence

from packages.domain.discovery.entities import DiscoveredJob
from packages.infrastructure.discovery.greenhouse.client import (
    GreenhouseClient,
)
from packages.infrastructure.discovery.greenhouse.mapper import (
    map_greenhouse_job,
)


class GreenhouseJobSource:
    """JobSource implementation backed by Greenhouse."""

    def __init__(self, client: GreenhouseClient) -> None:
        self._client = client

    @property
    def name(self) -> str:
        return "greenhouse"

    async def discover(self) -> Sequence[DiscoveredJob]:
        """Discover currently published Greenhouse jobs."""

        payloads = await self._client.list_jobs()

        discovered: list[DiscoveredJob] = []

        for payload in payloads:
            try:
                job = map_greenhouse_job(payload)
            except ValueError:
                continue

            discovered.append(job)

        return discovered
