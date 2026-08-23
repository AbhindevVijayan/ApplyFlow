from abc import ABC, abstractmethod
from uuid import UUID

from packages.domain.resumes.entities import Resume


class ResumeRepository(ABC):
    """Persistence contract for resume entities."""

    @abstractmethod
    async def create(self, resume: Resume) -> Resume:
        """Persist a new resume."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Return a resume by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        """Return all resumes belonging to a candidate."""
        raise NotImplementedError

    @abstractmethod
    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        """Return the canonical resume for a candidate."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, resume: Resume) -> Resume:
        """Update an existing resume."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, resume_id: UUID) -> None:
        """Delete a resume."""
        raise NotImplementedError
