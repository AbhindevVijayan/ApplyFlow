from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.candidates.education import CandidateEducation


class CandidateEducationRepository(Protocol):
    """Persistence contract for candidate education."""

    async def create(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Persist candidate education."""
        ...

    async def get_by_id(
        self,
        education_id: UUID,
    ) -> CandidateEducation | None:
        """Find education by ID."""
        ...

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Sequence[CandidateEducation]:
        """Return all education records for a candidate."""
        ...

    async def update(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Update candidate education."""
        ...

    async def delete(
        self,
        education_id: UUID,
    ) -> None:
        """Delete candidate education."""
        ...