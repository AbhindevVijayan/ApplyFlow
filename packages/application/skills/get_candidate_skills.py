from collections.abc import Sequence
from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.skills.entities import CandidateSkill
from packages.domain.skills.repository import SkillRepository


class CandidateNotFoundError(Exception):
    """Raised when the candidate does not exist."""


class GetCandidateSkills:
    """Use case for retrieving a candidate's skills."""

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
    ) -> Sequence[CandidateSkill]:
        """Return all skills associated with a candidate."""

        candidate = await self._candidate_repository.get_by_id(
            candidate_id,
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{candidate_id}' was not found.",
            )

        return await self._skill_repository.get_candidate_skills(
            candidate_id,
        )
