from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.candidates.experience import CandidateExperience


class CandidateExperienceRepository(Protocol):
    """Persistence contract for candidate professional experience."""

    async def create(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Persist candidate experience."""
        ...

    async def get_by_id(
        self,
        experience_id: UUID,
    ) -> CandidateExperience | None:
        """Find experience by ID."""
        ...

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Sequence[CandidateExperience]:
        """Return all experience records for a candidate."""
        ...

    async def update(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Update candidate experience."""
        ...

    async def delete(
        self,
        experience_id: UUID,
    ) -> None:
        """Delete candidate experience."""
        ...
