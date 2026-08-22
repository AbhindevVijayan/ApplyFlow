from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.resume import Resume


class ResumeRepository:
    """Persistence operations for Resume entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, resume: Resume) -> Resume:
        """Persist a new resume."""
        self._session.add(resume)
        await self._session.flush()
        await self._session.refresh(resume)

        return resume

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Return a resume by ID."""
        statement = select(Resume).where(Resume.id == resume_id)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        """Return all resumes belonging to a candidate."""
        statement = (
            select(Resume)
            .where(Resume.candidate_id == candidate_id)
            .order_by(Resume.created_at.desc())
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        """Return the canonical resume for a candidate."""
        statement = select(Resume).where(
            Resume.candidate_id == candidate_id,
            Resume.is_canonical.is_(True),
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def update(self, resume: Resume) -> Resume:
        """Persist changes to an existing resume."""
        existing = await self.get_by_id(resume.id)

        if existing is None:
            raise ValueError(f"Resume not found: {resume.id}")

        existing.candidate_id = resume.candidate_id
        existing.filename = resume.filename
        existing.content_type = resume.content_type
        existing.storage_key = resume.storage_key
        existing.parsed_text = resume.parsed_text
        existing.is_canonical = resume.is_canonical

        await self._session.flush()
        await self._session.refresh(existing)

        return existing

    async def delete(self, resume: Resume) -> None:
        """Delete a resume."""
        await self._session.delete(resume)
        await self._session.flush()
