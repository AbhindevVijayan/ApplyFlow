from dataclasses import dataclass
from uuid import uuid4

from packages.domain.skills.entities import Skill
from packages.domain.skills.repository import SkillRepository


class SkillAlreadyExistsError(Exception):
    """Raised when a skill with the same name already exists."""


@dataclass(frozen=True, slots=True)
class CreateSkillCommand:
    """Input required to create a skill."""

    name: str


class CreateSkill:
    """Use case for creating a skill."""

    def __init__(self, repository: SkillRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateSkillCommand,
    ) -> Skill:
        """Create and persist a skill."""

        existing = await self._repository.get_by_name(command.name)

        if existing is not None:
            raise SkillAlreadyExistsError(
                f"Skill with name '{command.name}' already exists.",
            )

        skill = Skill(
            id=uuid4(),
            name=command.name,
        )

        return await self._repository.create(skill)
