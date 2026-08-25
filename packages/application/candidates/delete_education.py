from uuid import UUID

from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class EducationNotFoundError(Exception):
    """Raised when education does not exist."""


class DeleteEducation:
    """Use case for deleting candidate education."""

    def __init__(
        self,
        repository: CandidateEducationRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        education_id: UUID,
    ) -> None:
        """Delete education by ID."""

        existing = await self._repository.get_by_id(
            education_id,
        )

        if existing is None:
            raise EducationNotFoundError(
                f"Education '{education_id}' was not found.",
            )

        await self._repository.delete(education_id)
