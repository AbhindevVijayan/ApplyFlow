from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.candidates.entities import Candidate


class CandidateRepository(Protocol):
    """Port for candidate persistence."""

    async def create(self, candidate: Candidate) -> Candidate:
        """Persist a candidate."""
        ...

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        """Find a candidate by ID."""
        ...

    async def get_by_email(self, email: str) -> Candidate | None:
        """Find a candidate by email."""
        ...

    async def update(self, candidate: Candidate) -> Candidate:
        """Persist changes to a candidate."""
        ...

    async def delete(self, candidate_id: UUID) -> None:
        """Delete a candidate."""
        ...

    async def list_all(self) -> Sequence[Candidate]:
        """Return all candidates."""
        ...
