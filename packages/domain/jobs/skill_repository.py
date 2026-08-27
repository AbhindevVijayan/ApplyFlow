from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.jobs.skill import JobSkill


class JobSkillRepository(Protocol):
    """Persistence contract for job-required skill associations."""

    async def add(
        self,
        job_skill: JobSkill,
    ) -> JobSkill:
        """Associate a required skill with a job."""
        ...

    async def get(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> JobSkill | None:
        """Return a job-skill association."""
        ...

    async def list_for_job(
        self,
        job_id: UUID,
    ) -> Sequence[JobSkill]:
        """Return all required skills for a job."""
        ...

    async def remove(
        self,
        job_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a required skill from a job."""
        ...
