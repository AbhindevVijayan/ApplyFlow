from collections.abc import Sequence
from uuid import UUID

from packages.domain.applications.entities import Application
from packages.domain.applications.repositories import ApplicationRepository


class ListApplications:
    """Use case for listing applications."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    async def by_candidate(
        self,
        candidate_id: UUID,
    ) -> Sequence[Application]:
        """Return applications belonging to a candidate."""

        return await self._repository.get_by_candidate_id(candidate_id)

    async def by_job(
        self,
        job_id: UUID,
    ) -> Sequence[Application]:
        """Return applications for a job."""

        return await self._repository.get_by_job_id(job_id)
