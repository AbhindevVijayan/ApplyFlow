from abc import ABC, abstractmethod
from uuid import UUID

from packages.domain.resumes.entities import Resume


class ResumeRepository(ABC):
    """Port for resume persistence."""

    @abstractmethod
    async def create(self, resume: Resume) -> Resume:
        """Create a resume."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Get a resume by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        """Get all resumes belonging to a candidate."""
        raise NotImplementedError

    @abstractmethod
    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        """Get the canonical resume for a candidate."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, resume: Resume) -> Resume:
        """Update a resume."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, resume_id: UUID) -> None:
        """Delete a resume."""
        raise NotImplementedError
