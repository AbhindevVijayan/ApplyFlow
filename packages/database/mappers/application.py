from packages.database.models.application import Application as ApplicationModel
from packages.domain.applications.entities import Application as ApplicationDomain
from packages.domain.applications.entities import ApplicationStatus


def to_domain(model: ApplicationModel) -> ApplicationDomain:
    """Convert a database application into a domain application."""

    return ApplicationDomain(
        id=model.id,
        candidate_id=model.candidate_id,
        job_id=model.job_id,
        resume_id=model.resume_id,
        status=ApplicationStatus(model.status),
        applied_at=model.applied_at,
        external_application_url=model.external_application_url,
        notes=model.notes,
        failure_reason=model.failure_reason,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(application: ApplicationDomain) -> ApplicationModel:
    """Convert a domain application into a database application."""

    return ApplicationModel(
        id=application.id,
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        applied_at=application.applied_at,
        external_application_url=application.external_application_url,
        notes=application.notes,
        failure_reason=application.failure_reason,
    )
