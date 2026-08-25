from uuid import UUID

from packages.domain.candidates.experience import CandidateExperience
from packages.domain.candidates.experience_repository import (
    CandidateExperienceRepository,
)


class ExperienceNotFoundError(Exception):
    """Raised when candidate experience does not exist."""


class GetExperience:
    """Use case for retrieving candidate experience."""

    def __init__(
        self,
        repository: CandidateExperienceRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        experience_id: UUID,
    ) -> CandidateExperience:
        """Return experience by ID."""

        experience = await self._repository.get_by_id(
            experience_id,
        )

        if experience is None:
            raise ExperienceNotFoundError(
                f"Candidate experience '{experience_id}' was not found.",
            )

        return experience
