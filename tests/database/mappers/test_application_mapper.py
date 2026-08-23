from datetime import UTC, datetime
from uuid import uuid4

from packages.database.mappers.application import to_domain, to_model
from packages.database.models.application import Application as ApplicationModel
from packages.domain.applications.entities import (
    Application as ApplicationDomain,
)
from packages.domain.applications.entities import (
    ApplicationStatus,
)


def test_to_domain() -> None:
    application_id = uuid4()
    candidate_id = uuid4()
    job_id = uuid4()
    resume_id = uuid4()
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)
    applied_at = datetime.now(UTC)

    model = ApplicationModel(
        id=application_id,
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status="submitted",
        applied_at=applied_at,
        external_application_url="https://example.com/application",
        notes="Application submitted successfully.",
        failure_reason=None,
    )

    model.created_at = created_at
    model.updated_at = updated_at

    domain = to_domain(model)

    assert domain.id == application_id
    assert domain.candidate_id == candidate_id
    assert domain.job_id == job_id
    assert domain.resume_id == resume_id
    assert domain.status is ApplicationStatus.SUBMITTED
    assert domain.applied_at == applied_at
    assert domain.external_application_url == "https://example.com/application"
    assert domain.notes == "Application submitted successfully."
    assert domain.failure_reason is None
    assert domain.created_at == created_at
    assert domain.updated_at == updated_at


def test_to_model() -> None:
    application_id = uuid4()
    candidate_id = uuid4()
    job_id = uuid4()
    resume_id = uuid4()
    applied_at = datetime.now(UTC)

    domain = ApplicationDomain(
        id=application_id,
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status=ApplicationStatus.READY,
        applied_at=applied_at,
        external_application_url="https://example.com/apply",
        notes="Ready for submission.",
        failure_reason=None,
    )

    model = to_model(domain)

    assert model.id == application_id
    assert model.candidate_id == candidate_id
    assert model.job_id == job_id
    assert model.resume_id == resume_id
    assert model.status == "ready"
    assert model.applied_at == applied_at
    assert model.external_application_url == "https://example.com/apply"
    assert model.notes == "Ready for submission."
    assert model.failure_reason is None
