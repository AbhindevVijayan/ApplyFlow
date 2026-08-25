from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.candidate import to_domain, to_model
from packages.database.repositories.candidate import (
    CandidateRepository as DatabaseCandidateRepository,
)
from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.repository import CandidateRepository


class CandidateRepositoryAdapter(CandidateRepository):
    """Adapt the SQLAlchemy candidate repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseCandidateRepository(session)

    async def create(self, candidate: Candidate) -> Candidate:
        """Persist a domain candidate."""
        model = to_model(candidate)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        """Find a candidate by ID."""
        model = await self._repository.get_by_id(candidate_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_email(self, email: str) -> Candidate | None:
        """Find a candidate by email."""
        model = await self._repository.get_by_email(email)

        if model is None:
            return None

        return to_domain(model)

    async def update(self, candidate: Candidate) -> Candidate:
        """Persist changes to an existing domain candidate."""

        model = await self._repository.get_by_id(candidate.id)

        if model is None:
            raise ValueError(
                f"Candidate '{candidate.id}' does not exist.",
            )

        model.full_name = candidate.full_name
        model.email = candidate.email
        model.phone = candidate.phone
        model.location = candidate.location

        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(self, candidate_id: UUID) -> None:
        """Delete a candidate by ID."""
        model = await self._repository.get_by_id(candidate_id)

        if model is None:
            return

        await self._repository.delete(model)

    async def list_all(self) -> Sequence[Candidate]:
        """Return all candidates."""
        models = await self._repository.list_all()

        return [to_domain(model) for model in models]
