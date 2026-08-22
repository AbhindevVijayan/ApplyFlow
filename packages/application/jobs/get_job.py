from uuid import UUID

from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


class JobNotFoundError(Exception):
    """Raised when the requested job does not exist."""


class GetJob:
    """Use case for retrieving a job."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        job_id: UUID,
    ) -> Job:
        """Retrieve a job by ID."""

        job = await self._repository.get_by_id(job_id)

        if job is None:
            raise JobNotFoundError(
                f"Job '{job_id}' was not found.",
            )

        return job
