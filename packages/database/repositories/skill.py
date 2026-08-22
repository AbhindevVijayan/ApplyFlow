from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.skill import CandidateSkill, Skill


class SkillRepository:
    """Persistence operations for Skill entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, skill: Skill) -> Skill:
        """Persist a new skill."""
        self._session.add(skill)
        await self._session.flush()
        await self._session.refresh(skill)

        return skill

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        """Return a skill by ID."""
        statement = select(Skill).where(Skill.id == skill_id)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Skill | None:
        """Return a skill by name."""
        statement = select(Skill).where(Skill.name == name)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Skill]:
        """Return all skills ordered by name."""
        statement = select(Skill).order_by(Skill.name)

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def update(self, skill: Skill) -> Skill:
        """Persist changes to an existing skill."""
        self._session.add(skill)
        await self._session.flush()
        await self._session.refresh(skill)

        return skill

    async def delete(self, skill: Skill) -> None:
        """Delete a skill."""
        await self._session.delete(skill)
        await self._session.flush()

    async def add_to_candidate(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Associate a skill with a candidate."""
        self._session.add(candidate_skill)
        await self._session.flush()
        await self._session.refresh(candidate_skill)

        return candidate_skill

    async def get_candidate_skill(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> CandidateSkill | None:
        """Return a candidate-skill association."""
        statement = select(CandidateSkill).where(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_candidate_skills(
        self,
        candidate_id: UUID,
    ) -> list[CandidateSkill]:
        """Return all skills associated with a candidate."""
        statement = (
            select(CandidateSkill)
            .where(CandidateSkill.candidate_id == candidate_id)
            .order_by(CandidateSkill.skill_id)
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def update_candidate_skill(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Persist changes to a candidate-skill association."""
        self._session.add(candidate_skill)
        await self._session.flush()
        await self._session.refresh(candidate_skill)

        return candidate_skill

    async def remove_from_candidate(
        self,
        candidate_skill: CandidateSkill,
    ) -> None:
        """Remove a skill association from a candidate."""
        await self._session.delete(candidate_skill)
        await self._session.flush()
