from dataclasses import dataclass
from datetime import date
from uuid import UUID

from packages.domain.candidates.experience import CandidateExperience
from packages.domain.candidates.experience_repository import (
    CandidateExperienceRepository,
)


class ExperienceNotFoundError(Exception):
    """Raised when candidate experience does not exist."""


class InvalidExperienceError(ValueError):
    """Raised when experience data violates domain rules."""


@dataclass(frozen=True, slots=True)
class UpdateExperienceCommand:
    """Data required to update candidate experience."""

    experience_id: UUID
    company_name: str
    job_title: str
    employment_type: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    is_current: bool = False


class UpdateExperience:
    """Use case for updating candidate experience."""

    def __init__(
        self,
        repository: CandidateExperienceRepository,
    ) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateExperienceCommand,
    ) -> CandidateExperience:
        """Validate and update candidate experience."""

        existing = await self._repository.get_by_id(
            command.experience_id,
        )

        if existing is None:
            raise ExperienceNotFoundError(
                f"Experience '{command.experience_id}' was not found.",
            )

        self._validate_dates(
            start_date=command.start_date,
            end_date=command.end_date,
            is_current=command.is_current,
        )

        updated = CandidateExperience(
            id=existing.id,
            candidate_id=existing.candidate_id,
            company_name=command.company_name,
            job_title=command.job_title,
            employment_type=command.employment_type,
            location=command.location,
            start_date=command.start_date,
            end_date=command.end_date,
            description=command.description,
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
                raise InvalidExperienceError(
                    "end_date cannot be earlier than start_date.",
                )

        if is_current and end_date is not None:
            raise InvalidExperienceError(
                "Current experience cannot have an end_date.",
            )
