from dataclasses import dataclass
from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.skills.entities import CandidateSkill
from packages.domain.skills.repository import SkillRepository


class CandidateNotFoundError(Exception):
    """Raised when the candidate does not exist."""


class SkillNotFoundError(Exception):
    """Raised when the skill does not exist."""


class CandidateSkillNotFoundError(Exception):
    """Raised when the candidate-skill association does not exist."""


@dataclass(frozen=True, slots=True)
class UpdateCandidateSkillCommand:
    """Input required to update a candidate's skill."""

    candidate_id: UUID
    skill_id: UUID
    proficiency: str | None


class UpdateCandidateSkill:
    """Use case for updating a candidate-skill association."""

    def __init__(
        self,
        skill_repository: SkillRepository,
        candidate_repository: CandidateRepository,
    ) -> None:
        self._skill_repository = skill_repository
        self._candidate_repository = candidate_repository

    async def execute(
        self,
        command: UpdateCandidateSkillCommand,
    ) -> CandidateSkill:
        """Update the proficiency of a candidate's skill."""

        candidate = await self._candidate_repository.get_by_id(
            command.candidate_id,
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{command.candidate_id}' was not found.",
            )

        skill = await self._skill_repository.get_by_id(
            command.skill_id,
        )

        if skill is None:
            raise SkillNotFoundError(
                f"Skill '{command.skill_id}' was not found.",
            )

        existing = await self._skill_repository.get_candidate_skill(
            command.candidate_id,
            command.skill_id,
        )

        if existing is None:
            raise CandidateSkillNotFoundError(
                f"Candidate '{command.candidate_id}' does not have skill '{command.skill_id}'.",
            )

        updated = CandidateSkill(
            candidate_id=existing.candidate_id,
            skill_id=existing.skill_id,
            proficiency=command.proficiency,
        )

        return await self._skill_repository.update_candidate_skill(
            updated,
        )
