from uuid import UUID

from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.repository import CandidateRepository


class CandidateNotFoundError(Exception):
    """Raised when the requested candidate does not exist."""


class GetCandidate:
    """Use case for retrieving a candidate."""

    def __init__(self, repository: CandidateRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        candidate_id: UUID,
    ) -> Candidate:
        """Retrieve a candidate by ID."""

        candidate = await self._repository.get_by_id(candidate_id)

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{candidate_id}' was not found.",
            )

        return candidate
