from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.skill import (
    job_skill_to_domain,
    job_skill_to_model,
)
from packages.database.repositories.job_skill import (
    JobSkillRepository as DatabaseJobSkillRepository,
)
from packages.domain.jobs.skill import JobSkill
from packages.domain.jobs.skill_repository import JobSkillRepository


class JobSkillRepositoryAdapter(JobSkillRepository):
    """Adapt the SQLAlchemy job-skill repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseJobSkillRepository(session)

    async def add(self, job_skill: JobSkill) -> JobSkill:
        """Persist a domain job-skill association."""
        model = job_skill_to_model(job_skill)

        created = await self._repository.add(model)

        return job_skill_to_domain(created)

    async def get(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> JobSkill | None:
        """Find a job-skill association."""
        model = await self._repository.get(job_id, skill_id)

        if model is None:
            return None

        return job_skill_to_domain(model)

    async def list_for_job(
        self,
        job_id: UUID,
    ) -> Sequence[JobSkill]:
        """Return all required skills for a job."""
        models = await self._repository.list_for_job(job_id)

        return [job_skill_to_domain(model) for model in models]

    async def remove(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a required skill from a job."""
        await self._repository.remove(job_id, skill_id)
