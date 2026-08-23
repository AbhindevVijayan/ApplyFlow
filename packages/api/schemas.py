from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from packages.domain.applications.entities import ApplicationStatus


class CreateCandidateRequest(BaseModel):
    """HTTP payload for creating a candidate."""

    full_name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None


class UpdateCandidateRequest(BaseModel):
    """HTTP payload for partially updating a candidate."""

    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None


class CandidateResponse(BaseModel):
    """HTTP representation of a candidate."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    phone: str | None
    location: str | None


class CreateResumeRequest(BaseModel):
    """HTTP payload for creating a resume."""

    candidate_id: UUID
    filename: str
    content_type: str
    storage_key: str
    parsed_text: str | None = None
    is_canonical: bool = False


class UpdateResumeRequest(BaseModel):
    """HTTP payload for updating a resume."""

    filename: str
    content_type: str
    storage_key: str
    parsed_text: str | None = None
    is_canonical: bool = False


class ResumeResponse(BaseModel):
    """HTTP representation of a resume."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    filename: str
    content_type: str
    storage_key: str
    parsed_text: str | None
    is_canonical: bool
    created_at: datetime | None


class CreateJobRequest(BaseModel):
    """HTTP payload for creating a job."""

    company: str
    title: str
    source: str
    source_url: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    discovered_at: datetime | None = None


class UpdateJobRequest(BaseModel):
    """HTTP payload for partially updating a job."""

    company: str | None = None
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    discovered_at: datetime | None = None


class JobResponse(BaseModel):
    """HTTP representation of a job."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company: str
    title: str
    source: str
    source_url: str
    description: str | None
    location: str | None
    employment_type: str | None
    discovered_at: datetime | None
    created_at: datetime | None


class CreateSkillRequest(BaseModel):
    """HTTP payload for creating a skill."""

    name: str


class SkillResponse(BaseModel):
    """HTTP representation of a skill."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class AddCandidateSkillRequest(BaseModel):
    """HTTP payload for assigning a skill to a candidate."""

    skill_id: UUID
    proficiency: str | None = None


class CandidateSkillResponse(BaseModel):
    """HTTP representation of a candidate-skill association."""

    candidate_id: UUID
    skill_id: UUID
    proficiency: str | None


class CreateApplicationRequest(BaseModel):
    """HTTP payload for creating a job application."""

    candidate_id: UUID
    job_id: UUID
    resume_id: UUID
    status: ApplicationStatus = ApplicationStatus.DRAFT
    applied_at: datetime | None = None
    external_application_url: str | None = None
    notes: str | None = None
    failure_reason: str | None = None


class UpdateApplicationRequest(BaseModel):
    """HTTP payload for partially updating a job application."""

    status: ApplicationStatus | None = None
    applied_at: datetime | None = None
    external_application_url: str | None = None
    notes: str | None = None
    failure_reason: str | None = None


class ApplicationResponse(BaseModel):
    """HTTP representation of a job application."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    job_id: UUID
    resume_id: UUID
    status: ApplicationStatus
    applied_at: datetime | None
    external_application_url: str | None
    notes: str | None
    failure_reason: str | None
    created_at: datetime | None
    updated_at: datetime | None
