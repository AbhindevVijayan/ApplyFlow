from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ApplicationStatus(StrEnum):
    """Lifecycle states for a job application."""

    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"


@dataclass(frozen=True, slots=True)
class Application:
    """Domain representation of a job application."""

    id: UUID
    candidate_id: UUID
    job_id: UUID
    resume_id: UUID
    status: ApplicationStatus = ApplicationStatus.DRAFT
    applied_at: datetime | None = None
    external_application_url: str | None = None
    notes: str | None = None
    failure_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
