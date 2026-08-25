from collections.abc import Sequence
from uuid import UUID
from packages.domain.jobs.repositories import JobRepository

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.job import to_domain
from packages.database.repositories.job import (
    JobRepository as DatabaseJobRepository,
)
from packages.domain.jobs.entities import Job


class JobRepositoryAdapter(JobRepository):
    """Adapt the SQLAlchemy job repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseJobRepository(session)

    async def create(self, job: Job) -> Job:
        """Persist a domain job."""
        from packages.database.mappers.job import to_model

        model = to_model(job)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(self, job_id: UUID) -> Job | None:
        """Find a job by ID."""
        model = await self._repository.get_by_id(job_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        """Find a job by source URL."""
        model = await self._repository.get_by_source_url(source_url)

        if model is None:
            return None

        return to_domain(model)

    async def list_all(self) -> Sequence[Job]:
        """Return all jobs."""
        models = await self._repository.list_all()

        return [to_domain(model) for model in models]

    async def update(self, job: Job) -> Job:
        """Update and persist a domain job."""
        model = await self._repository.get_by_id(job.id)

        if model is None:
            raise ValueError(
                f"Job '{job.id}' does not exist.",
            )

        model.company = job.company
        model.title = job.title
        model.source = job.source
        model.source_url = job.source_url
        model.description = job.description
        model.location = job.location
        model.employment_type = job.employment_type
        model.discovered_at = job.discovered_at

        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(self, job_id: UUID) -> None:
        """Delete a job by ID."""
        model = await self._repository.get_by_id(job_id)

        if model is None:
            return

        await self._repository.delete(model)
