from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ApplicationSubmissionContext:
    """Data required by an external application submission provider."""

    application_id: UUID

    candidate_id: UUID
    candidate_name: str
    candidate_email: str
    candidate_phone: str | None

    job_id: UUID
    job_title: str
    company: str
    source: str
    source_url: str

    resume_id: UUID
    resume_filename: str
    resume_storage_key: str
