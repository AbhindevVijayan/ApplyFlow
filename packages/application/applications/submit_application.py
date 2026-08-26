from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)
from packages.domain.applications.gateway import ApplicationSubmissionGateway
from packages.domain.applications.repositories import ApplicationRepository
from packages.domain.applications.submission import SubmissionStatus
from packages.domain.applications.submission_repositories import (
    ApplicationSubmissionContextRepository,
)


class ApplicationNotFoundError(Exception):
    """Raised when an application does not exist."""


class InvalidApplicationSubmissionError(Exception):
    """Raised when an application cannot be submitted."""


class ApplicationSubmissionContextNotFoundError(Exception):
    """Raised when submission context cannot be loaded."""


class SubmitApplication:
    """Submit an application through an external submission gateway."""

    def __init__(
        self,
        repository: ApplicationRepository,
        submission_context_repository: ApplicationSubmissionContextRepository,
        gateway: ApplicationSubmissionGateway,
    ) -> None:
        self._repository = repository
        self._submission_context_repository = submission_context_repository
        self._gateway = gateway

    async def execute(
        self,
        application_id: UUID,
    ) -> Application:
        """Submit an application and persist the resulting state."""

        application = await self._repository.get_by_id(application_id)

        if application is None:
            raise ApplicationNotFoundError(
                f"Application '{application_id}' was not found.",
            )

        if application.status not in {
            ApplicationStatus.READY,
        }:
            raise InvalidApplicationSubmissionError(
                f"Application '{application_id}' is not ready for submission.",
            )

        context = await self._submission_context_repository.get_by_application_id(
            application_id,
        )

        if context is None:
            raise ApplicationSubmissionContextNotFoundError(
                f"Submission context for application '{application_id}' was not found.",
            )

        result = await self._gateway.submit(context)

        if result.status == SubmissionStatus.SUBMITTED:
            updated_application = replace(
                application,
                status=ApplicationStatus.SUBMITTED,
                applied_at=application.applied_at or datetime.now(UTC),
                external_application_url=result.external_application_url,
                failure_reason=None,
            )
        else:
            updated_application = replace(
                application,
                status=ApplicationStatus.READY,
                failure_reason=result.failure_reason,
            )

        return await self._repository.update(updated_application)
