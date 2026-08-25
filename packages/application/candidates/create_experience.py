from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from packages.domain.candidates.experience import CandidateExperience
from packages.domain.candidates.experience_repository import (
    CandidateExperienceRepository,
)


class InvalidExperienceError(ValueError):
    """Raised when experience data violates domain rules."""


@dataclass(frozen=True, slots=True)
class CreateExperienceCommand:
    """Input required to create candidate experience."""

    candidate_id: UUID
    company_name: str
    job_title: str
    employment_type: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    is_current: bool = False


class CreateExperience:
    """Use case for creating candidate experience."""

    def __init__(
        self,
        repository: CandidateExperienceRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateExperienceCommand,
    ) -> CandidateExperience:
        """Validate, create, and persist experience."""

        self._validate_dates(
            start_date=command.start_date,
            end_date=command.end_date,
            is_current=command.is_current,
        )

        experience = CandidateExperience(
            id=uuid4(),
            candidate_id=command.candidate_id,
            company_name=command.company_name,
            job_title=command.job_title,
            employment_type=command.employment_type,
            location=command.location,
            start_date=command.start_date,
            end_date=command.end_date,
            description=command.description,
            is_current=command.is_current,
        )

        return await self._repository.create(experience)

    @staticmethod
    def _validate_dates(
        *,
        start_date: date | None,
        end_date: date | None,
        is_current: bool,
    ) -> None:
        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise InvalidExperienceError(
                    "end_date cannot be earlier than start_date.",
                )

        if is_current and end_date is not None:
            raise InvalidExperienceError(
                "Current experience cannot have an end_date.",
            )
