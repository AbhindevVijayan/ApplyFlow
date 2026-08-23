from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate_experience import CandidateExperience


class CandidateExperienceRepository:
    """Persistence operations for candidate professional experience."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Persist a new candidate experience record."""
        self._session.add(experience)
        await self._session.flush()
        await self._session.refresh(experience)

        return experience

    async def get_by_id(
        self,
        experience_id: UUID,
    ) -> CandidateExperience | None:
        """Return candidate experience by ID."""
        statement = select(CandidateExperience).where(
            CandidateExperience.id == experience_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        """Return all experience records for a candidate."""
        statement = (
            select(CandidateExperience)
            .where(
                CandidateExperience.candidate_id == candidate_id,
            )
            .order_by(
                CandidateExperience.start_date.desc(),
                CandidateExperience.id,
            )
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Persist changes to an existing experience record."""
        existing = await self.get_by_id(experience.id)

        if existing is None:
            raise ValueError(
                f"Candidate experience not found: {experience.id}",
            )

        existing.candidate_id = experience.candidate_id
        existing.company_name = experience.company_name
        existing.job_title = experience.job_title
        existing.employment_type = experience.employment_type
        existing.location = experience.location
        existing.start_date = experience.start_date
        existing.end_date = experience.end_date
        existing.description = experience.description
        existing.is_current = experience.is_current

        await self._session.flush()
        await self._session.refresh(existing)

        return existing

    async def delete(
        self,
        experience: CandidateExperience,
    ) -> None:
        """Delete candidate experience."""
        await self._session.delete(experience)
        await self._session.flush()
