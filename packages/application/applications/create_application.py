from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)
from packages.domain.applications.repositories import ApplicationRepository


class ApplicationAlreadyExistsError(Exception):
    """Raised when a candidate has already applied to a job."""


@dataclass(frozen=True, slots=True)
class CreateApplicationCommand:
    """Input required to create an application."""

    candidate_id: UUID
    job_id: UUID
    resume_id: UUID
    status: ApplicationStatus = ApplicationStatus.DRAFT
    applied_at: datetime | None = None
    external_application_url: str | None = None
    notes: str | None = None
    failure_reason: str | None = None


class CreateApplication:
    """Use case for creating a job application."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: CreateApplicationCommand,
    ) -> Application:
        """Create and persist an application."""

        existing = await self._repository.get_by_candidate_and_job(
            command.candidate_id,
            command.job_id,
        )

        if existing is not None:
            raise ApplicationAlreadyExistsError(
                "An application already exists for this candidate and job.",
            )

        application = Application(
            id=uuid4(),
            candidate_id=command.candidate_id,
            job_id=command.job_id,
            resume_id=command.resume_id,
            status=command.status,
            applied_at=command.applied_at,
            external_application_url=command.external_application_url,
            notes=command.notes,
            failure_reason=command.failure_reason,
        )

        return await self._repository.create(application)
