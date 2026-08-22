from collections.abc import Sequence

from packages.application.jobs.create_job import (
    CreateJob,
    CreateJobCommand,
    JobAlreadyExistsError,
)
from packages.domain.discovery.sources import JobSource
from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


class DiscoverJobs:
    """Discover jobs from an external source and persist new jobs."""

    def __init__(
        self,
        source: JobSource,
        repository: JobRepository,
    ) -> None:
        self._source = source
        self._repository = repository

    async def execute(self) -> Sequence[Job]:
        """Discover and persist jobs from the configured source."""

        discovered_jobs = await self._source.discover()

        create_job = CreateJob(self._repository)

        persisted_jobs: list[Job] = []

        for discovered in discovered_jobs:
            try:
                job = await create_job.execute(
                    CreateJobCommand(
                        company=discovered.company,
                        title=discovered.title,
                        source=discovered.source,
                        source_url=discovered.source_url,
                        description=discovered.description,
                        location=discovered.location,
                        employment_type=discovered.employment_type,
                        discovered_at=discovered.discovered_at,
                    ),
                )
            except JobAlreadyExistsError:
                continue

            persisted_jobs.append(job)

        return persisted_jobs
