from uuid import UUID

from packages.domain.skills.entities import Skill
from packages.domain.skills.repository import SkillRepository


class SkillNotFoundError(Exception):
    """Raised when the requested skill does not exist."""


class GetSkill:
    """Use case for retrieving a skill."""

    def __init__(self, repository: SkillRepository) -> None:
        self._repository = repository

    async def execute(self, skill_id: UUID) -> Skill:
        """Retrieve a skill by ID."""

        skill = await self._repository.get_by_id(skill_id)

        if skill is None:
            raise SkillNotFoundError(
                f"Skill '{skill_id}' was not found.",
            )

        return skill
