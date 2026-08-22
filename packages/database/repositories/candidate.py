from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate


class CandidateRepository:
    """Persistence operations for Candidate entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, candidate: Candidate) -> Candidate:
        """Persist a new candidate."""
        self._session.add(candidate)
        await self._session.flush()
        await self._session.refresh(candidate)

        return candidate

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        """Return a candidate by ID."""
        statement = select(Candidate).where(Candidate.id == candidate_id)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Candidate | None:
        """Return a candidate by email address."""
        statement = select(Candidate).where(Candidate.email == email)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def update(self, candidate: Candidate) -> Candidate:
        """Persist changes to an existing candidate."""
        self._session.add(candidate)
        await self._session.flush()
        await self._session.refresh(candidate)

        return candidate

    async def delete(self, candidate: Candidate) -> None:
        """Delete a candidate."""
        await self._session.delete(candidate)
        await self._session.flush()

    async def list_all(self) -> Sequence[Candidate]:
        """Return all candidates in deterministic order."""
        statement = select(Candidate).order_by(
            Candidate.created_at.asc(),
            Candidate.id.asc(),
        )

        result = await self._session.execute(statement)

        return result.scalars().all()
