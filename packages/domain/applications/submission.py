from dataclasses import dataclass
from enum import StrEnum


class SubmissionStatus(StrEnum):
    """Result of an external application submission attempt."""

    SUBMITTED = "submitted"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    """Result returned by an application submission provider."""

    status: SubmissionStatus
    external_application_url: str | None = None
    failure_reason: str | None = None
