from collections.abc import Sequence
from dataclasses import dataclass

from packages.application.discovery.discover_jobs import DiscoverJobs
from packages.domain.discovery.sources import JobSource
from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """Result of discovering jobs from a single source."""

    source: str
    jobs: tuple[Job, ...]


class RunDiscovery:
    """Run job discovery across multiple external sources."""

    def __init__(
        self,
        sources: Sequence[JobSource],
        repository: JobRepository,
    ) -> None:
        self._sources = sources
        self._repository = repository

    async def execute(self) -> Sequence[DiscoveryResult]:
        """Discover and persist jobs from all configured sources."""

        results: list[DiscoveryResult] = []

        for source in self._sources:
            discover_jobs = DiscoverJobs(
                source=source,
                repository=self._repository,
            )

            jobs = await discover_jobs.execute()

            results.append(
                DiscoveryResult(
                    source=source.name,
                    jobs=tuple(jobs),
                ),
            )

        return results
