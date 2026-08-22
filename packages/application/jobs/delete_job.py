from uuid import UUID

from packages.domain.jobs.repositories import JobRepository


class JobNotFoundError(Exception):
    """Raised when the requested job does not exist."""


class DeleteJob:
    """Use case for deleting a job."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(self, job_id: UUID) -> None:
        """Delete an existing job."""

        job = await self._repository.get_by_id(job_id)

        if job is None:
            raise JobNotFoundError(
                f"Job '{job_id}' was not found.",
            )

        await self._repository.delete(job_id)
