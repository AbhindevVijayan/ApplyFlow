from packages.database.models.job import Job as JobModel
from packages.domain.jobs.entities import Job


def to_domain(model: JobModel) -> Job:
    """Convert a database job into a domain job."""
    return Job(
        id=model.id,
        company=model.company,
        title=model.title,
        source=model.source,
        source_url=model.source_url,
        description=model.description,
        location=model.location,
        employment_type=model.employment_type,
        discovered_at=model.discovered_at,
        created_at=model.created_at,
    )


def to_model(job: Job) -> JobModel:
    """Convert a domain job into a database job."""
    model = JobModel(
        id=job.id,
        company=job.company,
        title=job.title,
        source=job.source,
        source_url=job.source_url,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        discovered_at=job.discovered_at,
    )

    return model
