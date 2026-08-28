from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.job_skill import JobSkill


class JobSkillRepository:
    """Persistence operations for job-required skill associations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, job_skill: JobSkill) -> JobSkill:
        """Persist a job-required skill association."""
        self._session.add(job_skill)
        await self._session.flush()
        await self._session.refresh(job_skill)

        return job_skill

    async def get(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> JobSkill | None:
        """Return a job-required skill association."""
        statement = select(JobSkill).where(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_for_job(
        self,
        job_id: UUID,
    ) -> Sequence[JobSkill]:
        """Return all required skills for a job."""
        statement = select(JobSkill).where(JobSkill.job_id == job_id).order_by(JobSkill.skill_id)

        result = await self._session.execute(statement)

        return result.scalars().all()

    async def remove(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a job-required skill association."""
        job_skill = await self.get(job_id, skill_id)

        if job_skill is None:
            return

        await self._session.delete(job_skill)
        await self._session.flush()
