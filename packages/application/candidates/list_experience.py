from uuid import UUID

from packages.domain.candidates.experience import CandidateExperience
from packages.domain.candidates.experience_repository import (
    CandidateExperienceRepository,
)


class ListExperience:
    """Use case for listing candidate professional experience."""

    def __init__(
        self,
        repository: CandidateExperienceRepository,
    ) -> None:
        self._repository = repository

    async def by_candidate(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        """Return all experience records for a candidate."""

        experiences = await self._repository.get_by_candidate_id(
            candidate_id,
        )

        return list(experiences)
