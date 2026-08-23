from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.candidate_education import (
    to_domain,
    to_model,
)
from packages.database.repositories.candidate_education import (
    CandidateEducationRepository as DatabaseCandidateEducationRepository,
)
from packages.domain.candidates.education import CandidateEducation
from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class CandidateEducationRepositoryAdapter(
    CandidateEducationRepository,
):
    """Adapt SQLAlchemy candidate education persistence to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseCandidateEducationRepository(session)

    async def create(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Persist domain education."""
        model = to_model(education)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(
        self,
        education_id: UUID,
    ) -> CandidateEducation | None:
        """Find education by ID."""
        model = await self._repository.get_by_id(education_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateEducation]:
        """Return education belonging to a candidate."""
        models = await self._repository.get_by_candidate_id(
            candidate_id,
        )

        return [to_domain(model) for model in models]

    async def update(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        """Persist changes to domain education."""
        model = to_model(education)
        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(
        self,
        education_id: UUID,
    ) -> None:
        """Delete education by ID."""
        model = await self._repository.get_by_id(education_id)

        if model is None:
            return

        await self._repository.delete(model)
