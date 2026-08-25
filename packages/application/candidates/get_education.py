from uuid import UUID

from packages.domain.candidates.education import CandidateEducation
from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class EducationNotFoundError(Exception):
    """Raised when education does not exist."""


class GetEducation:
    """Use case for retrieving candidate education."""

    def __init__(self, repository: CandidateEducationRepository) -> None:
        self._repository = repository

    async def execute(self, education_id: UUID) -> CandidateEducation:
        education = await self._repository.get_by_id(education_id)

        if education is None:
            raise EducationNotFoundError(
                f"Candidate education '{education_id}' was not found.",
            )

        return education
