from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.skill import (
    candidate_skill_to_domain,
    candidate_skill_to_model,
    skill_to_domain,
    skill_to_model,
)
from packages.database.repositories.skill import (
    SkillRepository as DatabaseSkillRepository,
)
from packages.domain.skills.entities import CandidateSkill, Skill
from packages.domain.skills.repository import SkillRepository


class SkillRepositoryAdapter(SkillRepository):
    """Adapt the SQLAlchemy skill repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseSkillRepository(session)

    async def create(self, skill: Skill) -> Skill:
        """Persist a domain skill."""
        model = skill_to_model(skill)

        created = await self._repository.create(model)

        return skill_to_domain(created)

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        """Find a skill by ID."""
        model = await self._repository.get_by_id(skill_id)

        if model is None:
            return None

        return skill_to_domain(model)

    async def get_by_name(self, name: str) -> Skill | None:
        """Find a skill by name."""
        model = await self._repository.get_by_name(name)

        if model is None:
            return None

        return skill_to_domain(model)

    async def list_all(self) -> Sequence[Skill]:
        """Return all skills."""
        models = await self._repository.get_all()

        return [skill_to_domain(model) for model in models]

    async def update(self, skill: Skill) -> Skill:
        """Update and persist a domain skill."""
        model = await self._repository.get_by_id(skill.id)

        if model is None:
            raise ValueError(
                f"Skill '{skill.id}' does not exist.",
            )

        model.name = skill.name

        updated = await self._repository.update(model)

        return skill_to_domain(updated)

    async def delete(self, skill_id: UUID) -> None:
        """Delete a skill by ID."""
        model = await self._repository.get_by_id(skill_id)

        if model is None:
            return

        await self._repository.delete(model)

    async def add_to_candidate(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Associate a skill with a candidate."""
        model = candidate_skill_to_model(candidate_skill)

        created = await self._repository.add_to_candidate(model)

        return candidate_skill_to_domain(created)

    async def get_candidate_skill(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> CandidateSkill | None:
        """Find a candidate-skill association."""
        model = await self._repository.get_candidate_skill(
            candidate_id,
            skill_id,
        )

        if model is None:
            return None

        return candidate_skill_to_domain(model)

    async def get_candidate_skills(
        self,
        candidate_id: UUID,
    ) -> Sequence[CandidateSkill]:
        """Return all skills associated with a candidate."""
        models = await self._repository.get_candidate_skills(
            candidate_id,
        )

        return [candidate_skill_to_domain(model) for model in models]

    async def update_candidate_skill(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Update a candidate-skill association."""
        model = await self._repository.get_candidate_skill(
            candidate_skill.candidate_id,
            candidate_skill.skill_id,
        )

        if model is None:
            raise ValueError(
                "Candidate-skill association does not exist.",
            )

        model.proficiency = candidate_skill.proficiency

        updated = await self._repository.update_candidate_skill(
            model,
        )

        return candidate_skill_to_domain(updated)

    async def remove_from_candidate(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a skill association from a candidate."""
        model = await self._repository.get_candidate_skill(
            candidate_id,
            skill_id,
        )

        if model is None:
            return

        await self._repository.remove_from_candidate(model)
