from dataclasses import dataclass
from typing import Final, TypeGuard
from uuid import UUID

from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.repository import CandidateRepository


class Unset:
    """Sentinel representing an omitted update field."""


UNSET: Final = Unset()


def is_set(value: str | Unset) -> TypeGuard[str]:
    """Return True when a required string field was supplied."""
    return not isinstance(value, Unset)


def is_optional_set(value: str | None | Unset) -> TypeGuard[str | None]:
    """Return True when an optional string field was supplied."""
    return not isinstance(value, Unset)


class CandidateNotFoundError(Exception):
    """Raised when the candidate does not exist."""


class CandidateEmailAlreadyExistsError(Exception):
    """Raised when the requested email belongs to another candidate."""


@dataclass(frozen=True, slots=True)
class UpdateCandidateCommand:
    """Fields that may be changed on a candidate."""

    candidate_id: UUID
    full_name: str | Unset = UNSET
    email: str | Unset = UNSET
    phone: str | None | Unset = UNSET
    location: str | None | Unset = UNSET


class UpdateCandidate:
    """Use case for updating a candidate."""

    def __init__(self, repository: CandidateRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateCandidateCommand,
    ) -> Candidate:
        """Update and persist a candidate."""

        candidate = await self._repository.get_by_id(
            command.candidate_id,
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{command.candidate_id}' was not found.",
            )

        if is_set(command.email) and command.email != candidate.email:
            existing = await self._repository.get_by_email(command.email)

            if existing is not None and existing.id != candidate.id:
                raise CandidateEmailAlreadyExistsError(
                    f"Candidate with email '{command.email}' already exists.",
                )

        full_name = command.full_name if is_set(command.full_name) else candidate.full_name

        email = command.email if is_set(command.email) else candidate.email

        phone = command.phone if is_optional_set(command.phone) else candidate.phone

        location = command.location if is_optional_set(command.location) else candidate.location

        updated = Candidate(
            id=candidate.id,
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            profile=candidate.profile,
        )

        return await self._repository.update(updated)
