from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.resume import to_domain, to_model
from packages.database.repositories.resume import (
    ResumeRepository as DatabaseResumeRepository,
)
from packages.domain.resumes.entities import Resume
from packages.domain.resumes.repository import ResumeRepository


class ResumeRepositoryAdapter(ResumeRepository):
    """Adapt the SQLAlchemy resume repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseResumeRepository(session)

    async def create(self, resume: Resume) -> Resume:
        """Persist a domain resume."""
        model = to_model(resume)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Find a resume by ID."""
        model = await self._repository.get_by_id(resume_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        """Return resumes belonging to a candidate."""
        models = await self._repository.get_by_candidate_id(candidate_id)

        return [to_domain(model) for model in models]

    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        """Return the canonical resume for a candidate."""
        model = await self._repository.get_canonical_by_candidate_id(
            candidate_id,
        )

        if model is None:
            return None

        return to_domain(model)

    async def update(self, resume: Resume) -> Resume:
        """Persist changes to a domain resume."""
        model = to_model(resume)
        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(self, resume_id: UUID) -> None:
        """Delete a resume by ID."""
        model = await self._repository.get_by_id(resume_id)

        if model is None:
            return

        await self._repository.delete(model)
