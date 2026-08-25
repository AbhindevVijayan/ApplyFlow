from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from packages.domain.candidates.education import CandidateEducation
from packages.domain.candidates.education_repository import (
    CandidateEducationRepository,
)


class InvalidEducationError(ValueError):
    """Raised when education data violates domain rules."""


@dataclass(frozen=True, slots=True)
class CreateEducationCommand:
    """Input required to create candidate education."""

    candidate_id: UUID
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    grade: str | None = None
    is_current: bool = False


class CreateEducation:
    """Use case for creating candidate education."""

    def __init__(
        self,
        repository: CandidateEducationRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateEducationCommand,
    ) -> CandidateEducation:
        """Validate, create, and persist education."""

        self._validate_dates(
            start_date=command.start_date,
            end_date=command.end_date,
            is_current=command.is_current,
        )

        education = CandidateEducation(
            id=uuid4(),
            candidate_id=command.candidate_id,
            institution=command.institution,
            degree=command.degree,
            field_of_study=command.field_of_study,
            start_date=command.start_date,
            end_date=command.end_date,
            grade=command.grade,
            is_current=command.is_current,
        )

        return await self._repository.create(education)

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
