from dataclasses import dataclass
from datetime import datetime
from typing import Final, TypeGuard
from uuid import UUID

from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)
from packages.domain.applications.repositories import ApplicationRepository


class Unset:
    """Sentinel representing an omitted update field."""


UNSET: Final = Unset()


def is_status_set(
    value: ApplicationStatus | Unset,
) -> TypeGuard[ApplicationStatus]:
    """Return True when a status was supplied."""

    return not isinstance(value, Unset)


def is_optional_string_set(
    value: str | None | Unset,
) -> TypeGuard[str | None]:
    """Return True when an optional string was supplied."""

    return not isinstance(value, Unset)


class ApplicationNotFoundError(Exception):
    """Raised when the requested application does not exist."""


class InvalidApplicationTransitionError(Exception):
    """Raised when an application status transition is invalid."""


@dataclass(frozen=True, slots=True)
class UpdateApplicationCommand:
    """Fields that may be changed on an application."""

    application_id: UUID
    status: ApplicationStatus | Unset = UNSET
    applied_at: datetime | None | Unset = UNSET
    external_application_url: str | None | Unset = UNSET
    notes: str | None | Unset = UNSET
    failure_reason: str | None | Unset = UNSET


ALLOWED_TRANSITIONS: dict[
    ApplicationStatus,
    frozenset[ApplicationStatus],
] = {
    ApplicationStatus.DRAFT: frozenset(
        {
            ApplicationStatus.READY,
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.READY: frozenset(
        {
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.SUBMITTED: frozenset(
        {
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.INTERVIEW: frozenset(
        {
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.OFFER: frozenset(
        {
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.REJECTED: frozenset(),
    ApplicationStatus.WITHDRAWN: frozenset(),
}


class UpdateApplication:
    """Use case for updating an application."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateApplicationCommand,
    ) -> Application:
        """Update and persist an application."""

        application = await self._repository.get_by_id(
            command.application_id,
        )

        if application is None:
            raise ApplicationNotFoundError(
                f"Application '{command.application_id}' was not found.",
            )

        status = application.status

        if is_status_set(command.status):
            requested_status = command.status

            if requested_status != application.status:
                allowed = ALLOWED_TRANSITIONS[application.status]

                if requested_status not in allowed:
                    raise InvalidApplicationTransitionError(
                        (
                            f"Cannot transition application from "
                            f"'{application.status}' to "
                            f"'{requested_status}'."
                        ),
                    )

                status = requested_status

        applied_at = (
            command.applied_at
            if not isinstance(command.applied_at, Unset)
            else application.applied_at
        )

        external_application_url = (
            command.external_application_url
            if is_optional_string_set(command.external_application_url)
            else application.external_application_url
        )

        notes = command.notes if is_optional_string_set(command.notes) else application.notes

        failure_reason = (
            command.failure_reason
            if is_optional_string_set(command.failure_reason)
            else application.failure_reason
        )

        updated = Application(
            id=application.id,
            candidate_id=application.candidate_id,
            job_id=application.job_id,
            resume_id=application.resume_id,
            status=status,
            applied_at=applied_at,
            external_application_url=external_application_url,
            notes=notes,
            failure_reason=failure_reason,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )

        return await self._repository.update(updated)
