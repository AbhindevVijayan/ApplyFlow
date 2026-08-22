from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository


class CandidateNotFoundError(Exception):
    """Raised when the requested candidate does not exist."""


class DeleteCandidate:
    """Use case for deleting a candidate."""

    def __init__(self, repository: CandidateRepository) -> None:
        self._repository = repository

    async def execute(self, candidate_id: UUID) -> None:
        """Delete an existing candidate."""

        candidate = await self._repository.get_by_id(candidate_id)

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{candidate_id}' was not found.",
            )

        await self._repository.delete(candidate_id)
