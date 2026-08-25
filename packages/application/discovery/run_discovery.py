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
    status: str
    jobs: tuple[Job, ...]
    discovered_count: int
    persisted_count: int
    duplicate_count: int
    error: str | None = None


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
            try:
                discover_jobs = DiscoverJobs(
                    source=source,
                    repository=self._repository,
                )

                result = await discover_jobs.execute()

            except Exception as exc:
                results.append(
                    DiscoveryResult(
                        source=source.name,
                        status="failed",
                        jobs=(),
                        discovered_count=0,
                        persisted_count=0,
                        duplicate_count=0,
                        error=str(exc),
                    ),
                )
                continue

            results.append(
                DiscoveryResult(
                    source=source.name,
                    status="completed",
                    jobs=result.jobs,
                    discovered_count=result.discovered_count,
                    persisted_count=result.persisted_count,
                    duplicate_count=result.duplicate_count,
                ),
            )

        return results
