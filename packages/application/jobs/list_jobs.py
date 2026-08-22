from collections.abc import Sequence

from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


class ListJobs:
    """Use case for retrieving all jobs."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(self) -> Sequence[Job]:
        """Return all persisted jobs."""
        return await self._repository.list_all()
