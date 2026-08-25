from dataclasses import dataclass
from datetime import date
from uuid import UUID

from packages.domain.candidates.education import CandidateEducation
from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class EducationNotFoundError(Exception):
    """Raised when education does not exist."""


class InvalidEducationError(ValueError):
    """Raised when education data violates domain rules."""


@dataclass(frozen=True, slots=True)
class UpdateEducationCommand:
    """Data required to update education."""

    education_id: UUID
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    grade: str | None = None
    is_current: bool = False


class UpdateEducation:
    """Use case for updating candidate education."""

    def __init__(
        self,
        repository: CandidateEducationRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateEducationCommand,
    ) -> CandidateEducation:
        """Validate and update education."""

        existing = await self._repository.get_by_id(
            command.education_id,
        )

        if existing is None:
            raise EducationNotFoundError(
                f"Education '{command.education_id}' was not found.",
            )

        self._validate_dates(
            start_date=command.start_date,
            end_date=command.end_date,
            is_current=command.is_current,
        )

        updated = CandidateEducation(
            id=existing.id,
            candidate_id=existing.candidate_id,
            institution=command.institution,
            degree=command.degree,
            field_of_study=command.field_of_study,
            start_date=command.start_date,
            end_date=command.end_date,
            grade=command.grade,
            is_current=command.is_current,
        )

        return await self._repository.update(updated)

    @staticmethod
    def _validate_dates(
        *,
        start_date: date | None,
        end_date: date | None,
        is_current: bool,
    ) -> None:
        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise InvalidEducationError(
                    "end_date cannot be earlier than start_date.",
                )

        if is_current and end_date is not None:
            raise InvalidEducationError(
                "Current education cannot have an end_date.",
            )
