from collections.abc import Mapping
from typing import Final

from packages.domain.applications.entities import ApplicationStatus


class InvalidApplicationTransitionError(ValueError):
    """Raised when an application status transition is not allowed."""


ALLOWED_TRANSITIONS: Final[Mapping[ApplicationStatus, frozenset[ApplicationStatus]]] = {
    ApplicationStatus.DRAFT: frozenset(
        {
            ApplicationStatus.READY,
            ApplicationStatus.WITHDRAWN,
        }
    ),
    ApplicationStatus.READY: frozenset(
        {
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.WITHDRAWN,
        }
    ),
    ApplicationStatus.SUBMITTED: frozenset(
        {
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        }
    ),
    ApplicationStatus.INTERVIEW: frozenset(
        {
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        }
    ),
    ApplicationStatus.OFFER: frozenset(
        {
            ApplicationStatus.WITHDRAWN,
        },
    ),
    ApplicationStatus.REJECTED: frozenset(),
    ApplicationStatus.WITHDRAWN: frozenset(),
}


def can_transition(
    current_status: ApplicationStatus,
    target_status: ApplicationStatus,
) -> bool:
    """Return whether an application can move to the target status."""

    if current_status == target_status:
        return True

    return target_status in ALLOWED_TRANSITIONS[current_status]


def validate_transition(
    current_status: ApplicationStatus,
    target_status: ApplicationStatus,
) -> None:
    """Validate an application status transition."""

    if can_transition(current_status, target_status):
        return

    raise InvalidApplicationTransitionError(
        f"Invalid application status transition: {current_status.value} -> {target_status.value}."
    )
