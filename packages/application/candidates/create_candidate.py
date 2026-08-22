from dataclasses import dataclass
from uuid import uuid4

from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.repository import CandidateRepository


class CandidateAlreadyExistsError(Exception):
    """Raised when a candidate with the same email already exists."""


@dataclass(frozen=True, slots=True)
class CreateCandidateCommand:
    """Input required to create a candidate."""

    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None


class CreateCandidate:
    """Use case for creating a candidate."""

    def __init__(self, repository: CandidateRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateCandidateCommand,
    ) -> Candidate:
        """Create and persist a candidate."""

        existing = await self._repository.get_by_email(command.email)

        if existing is not None:
            raise CandidateAlreadyExistsError(
                f"Candidate with email '{command.email}' already exists.",
            )

        candidate = Candidate(
            id=uuid4(),
            full_name=command.full_name,
            email=command.email,
            phone=command.phone,
            location=command.location,
        )

        return await self._repository.create(candidate)
