from uuid import UUID

from packages.domain.candidates.education import CandidateEducation
from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class ListEducation:
    """Use case for listing candidate education."""

    def __init__(
        self,
        repository: CandidateEducationRepository,
    ) -> None:
        self._repository = repository

    async def by_candidate(
        self,
        candidate_id: UUID,
    ) -> list[CandidateEducation]:
        """Return all education records for a candidate."""

        education = await self._repository.get_by_candidate_id(
            candidate_id,
        )

        return list(education)
