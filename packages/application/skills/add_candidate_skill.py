from dataclasses import dataclass
from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.skills.entities import CandidateSkill
from packages.domain.skills.repository import SkillRepository


class CandidateNotFoundError(Exception):
    """Raised when the candidate does not exist."""


class SkillNotFoundError(Exception):
    """Raised when the skill does not exist."""


class CandidateSkillAlreadyExistsError(Exception):
    """Raised when the candidate already has the skill."""


@dataclass(frozen=True, slots=True)
class AddCandidateSkillCommand:
    """Input required to associate a skill with a candidate."""

    candidate_id: UUID
    skill_id: UUID
    proficiency: str | None = None


class AddCandidateSkill:
    """Use case for assigning a skill to a candidate."""

    def __init__(
        self,
        skill_repository: SkillRepository,
        candidate_repository: CandidateRepository,
    ) -> None:
        self._skill_repository = skill_repository
        self._candidate_repository = candidate_repository

    async def execute(
        self,
        command: AddCandidateSkillCommand,
    ) -> CandidateSkill:
        """Validate and create a candidate-skill association."""

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

        if existing is not None:
            raise CandidateSkillAlreadyExistsError(
                f"Candidate '{command.candidate_id}' already has skill '{command.skill_id}'.",
            )

        candidate_skill = CandidateSkill(
            candidate_id=command.candidate_id,
            skill_id=command.skill_id,
            proficiency=command.proficiency,
        )

        return await self._skill_repository.add_to_candidate(
            candidate_skill,
        )
