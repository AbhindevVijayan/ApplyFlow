from dataclasses import dataclass

from packages.application.jobs.create_job import (
    CreateJob,
    CreateJobCommand,
    JobAlreadyExistsError,
)
from packages.domain.discovery.sources import JobSource
from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository
from packages.domain.requirements.extractor import JobRequirementsExtractor


@dataclass(frozen=True, slots=True)
class DiscoverJobsResult:
    """Result of discovering jobs from a single source."""

    jobs: tuple[Job, ...]
    discovered_count: int
    persisted_count: int
    duplicate_count: int


class DiscoverJobs:
    """Discover jobs from an external source and persist new jobs."""

    def __init__(
        self,
        source: JobSource,
        repository: JobRepository,
        requirements_extractor: JobRequirementsExtractor,
    ) -> None:
        self._source = source
        self._repository = repository
        self._requirements_extractor = requirements_extractor

    async def execute(self) -> DiscoverJobsResult:
        """Discover and persist new jobs from the configured source."""

        discovered_jobs = await self._source.discover()

        create_job = CreateJob(self._repository)

        persisted_jobs: list[Job] = []
        duplicate_count = 0

        for discovered in discovered_jobs:
            requirements = self._requirements_extractor.extract(
                discovered.description,
            )

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
                        required_skills=requirements.required_skills,
                        discovered_at=discovered.discovered_at,
                    ),
                )
            except JobAlreadyExistsError:
                duplicate_count += 1
                continue

            persisted_jobs.append(job)

        return DiscoverJobsResult(
            jobs=tuple(persisted_jobs),
            discovered_count=len(discovered_jobs),
            persisted_count=len(persisted_jobs),
            duplicate_count=duplicate_count,
        )
