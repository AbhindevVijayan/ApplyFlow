from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.candidate_experience import (
    to_domain,
    to_model,
)
from packages.database.repositories.candidate_experience import (
    CandidateExperienceRepository as DatabaseCandidateExperienceRepository,
)
from packages.domain.candidates.experience import CandidateExperience
from packages.domain.candidates.experience_repository import (
    CandidateExperienceRepository,
)


class CandidateExperienceRepositoryAdapter(
    CandidateExperienceRepository,
):
    """Adapt SQLAlchemy candidate experience persistence to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseCandidateExperienceRepository(session)

    async def create(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Persist domain experience."""
        model = to_model(experience)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(
        self,
        experience_id: UUID,
    ) -> CandidateExperience | None:
        """Find experience by ID."""
        model = await self._repository.get_by_id(experience_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        """Return experience belonging to a candidate."""
        models = await self._repository.get_by_candidate_id(
            candidate_id,
        )

        return [to_domain(model) for model in models]

    async def update(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        """Persist changes to domain experience."""
        model = to_model(experience)
        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(
        self,
        experience_id: UUID,
    ) -> None:
        """Delete experience by ID."""
        model = await self._repository.get_by_id(experience_id)

        if model is None:
            return

        await self._repository.delete(model)
