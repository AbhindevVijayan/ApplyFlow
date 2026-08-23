from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.skills.repository import SkillRepository


class CandidateNotFoundError(Exception):
    """Raised when the candidate does not exist."""


class SkillNotFoundError(Exception):
    """Raised when the skill does not exist."""


class CandidateSkillNotFoundError(Exception):
    """Raised when the candidate-skill association does not exist."""


class RemoveCandidateSkill:
    """Use case for removing a skill from a candidate."""

    def __init__(
        self,
        skill_repository: SkillRepository,
        candidate_repository: CandidateRepository,
    ) -> None:
        self._skill_repository = skill_repository
        self._candidate_repository = candidate_repository

    async def execute(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a skill association from a candidate."""

        candidate = await self._candidate_repository.get_by_id(
            candidate_id,
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{candidate_id}' was not found.",
            )

        skill = await self._skill_repository.get_by_id(
            skill_id,
        )

        if skill is None:
            raise SkillNotFoundError(
                f"Skill '{skill_id}' was not found.",
            )

        existing = await self._skill_repository.get_candidate_skill(
            candidate_id,
            skill_id,
        )

        if existing is None:
            raise CandidateSkillNotFoundError(
                f"Candidate '{candidate_id}' does not have skill '{skill_id}'.",
            )

        await self._skill_repository.remove_from_candidate(
            candidate_id,
            skill_id,
        )
