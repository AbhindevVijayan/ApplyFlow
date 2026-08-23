from collections.abc import Sequence

from packages.domain.skills.entities import Skill
from packages.domain.skills.repository import SkillRepository


class ListSkills:
    """Use case for listing skills."""

    def __init__(self, repository: SkillRepository) -> None:
        self._repository = repository

    async def execute(self) -> Sequence[Skill]:
        """Return all skills."""

        return await self._repository.list_all()
