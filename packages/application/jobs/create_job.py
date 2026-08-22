from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


class JobAlreadyExistsError(Exception):
    """Raised when a job with the same source URL already exists."""


@dataclass(frozen=True, slots=True)
class CreateJobCommand:
    """Input required to create a job."""

    company: str
    title: str
    source: str
    source_url: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    discovered_at: datetime | None = None


class CreateJob:
    """Use case for creating a job."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateJobCommand,
    ) -> Job:
        """Create and persist a job."""

        existing = await self._repository.get_by_source_url(
            command.source_url,
        )

        if existing is not None:
            raise JobAlreadyExistsError(
                f"Job with source URL '{command.source_url}' already exists.",
            )

        job = Job(
            id=uuid4(),
            company=command.company,
            title=command.title,
            source=command.source,
            source_url=command.source_url,
            description=command.description,
            location=command.location,
            employment_type=command.employment_type,
            discovered_at=command.discovered_at,
        )

        return await self._repository.create(job)
