from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate_education import CandidateEducation


class CandidateEducationRepository:
    """Persistence operations for candidate education entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Persist a new education record."""
        self._session.add(education)
        await self._session.flush()
        await self._session.refresh(education)

        return education

    async def get_by_id(
        self,
        education_id: UUID,
    ) -> CandidateEducation | None:
        """Return education by ID."""
        statement = select(CandidateEducation).where(
            CandidateEducation.id == education_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateEducation]:
        """Return all education records for a candidate."""
        statement = (
            select(CandidateEducation)
            .where(
                CandidateEducation.candidate_id == candidate_id,
            )
            .order_by(
                CandidateEducation.start_date.desc(),
                CandidateEducation.id,
            )
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Persist changes to an existing education record."""
        existing = await self.get_by_id(education.id)

        if existing is None:
            raise ValueError(
                f"Candidate education not found: {education.id}",
            )

        existing.candidate_id = education.candidate_id
        existing.institution = education.institution
        existing.degree = education.degree
        existing.field_of_study = education.field_of_study
        existing.start_date = education.start_date
        existing.end_date = education.end_date
        existing.grade = education.grade
        existing.is_current = education.is_current

        await self._session.flush()
        await self._session.refresh(existing)

        return existing

    async def delete(
        self,
        education: CandidateEducation,
    ) -> None:
        """Delete candidate education."""
        await self._session.delete(education)
        await self._session.flush()
