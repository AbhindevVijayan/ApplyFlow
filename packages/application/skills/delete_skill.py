from uuid import UUID

from packages.domain.skills.repository import SkillRepository


class SkillNotFoundError(Exception):
    """Raised when the requested skill does not exist."""


class DeleteSkill:
    """Use case for deleting a skill."""

    def __init__(self, repository: SkillRepository) -> None:
        self._repository = repository

    async def execute(self, skill_id: UUID) -> None:
        """Delete an existing skill."""

        skill = await self._repository.get_by_id(skill_id)

        if skill is None:
            raise SkillNotFoundError(
                f"Skill '{skill_id}' was not found.",
            )

        await self._repository.delete(skill_id)
