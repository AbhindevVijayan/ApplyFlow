from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.job import Job


class JobRepository:
    """Persistence operations for Job entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, job: Job) -> Job:
        """Persist a new job."""
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)

        return job

    async def get_by_id(self, job_id: UUID) -> Job | None:
        """Return a job by ID."""
        statement = select(Job).where(Job.id == job_id)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        """Return a job by its source URL."""
        statement = select(Job).where(
            Job.source_url == source_url,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Job]:
        """Return all jobs in deterministic order."""
        statement = select(Job).order_by(
            Job.created_at.asc(),
            Job.id.asc(),
        )

        result = await self._session.execute(statement)

        return result.scalars().all()

    async def update(self, job: Job) -> Job:
        """Persist changes to an existing job."""
        await self._session.flush()
        await self._session.refresh(job)

        return job

    async def delete(self, job: Job) -> None:
        """Delete a job."""
        await self._session.delete(job)
        await self._session.flush()
