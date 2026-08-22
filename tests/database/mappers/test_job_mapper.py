from datetime import UTC, datetime
from uuid import uuid4

from packages.database.mappers.job import to_domain, to_model
from packages.database.models.job import Job as JobModel
from packages.domain.jobs.entities import Job


def test_to_domain_maps_all_fields() -> None:
    job_id = uuid4()
    discovered_at = datetime.now(UTC)
    created_at = datetime.now(UTC)

    model = JobModel(
        id=job_id,
        company="Acme",
        title="Python Developer",
        source="LinkedIn",
        source_url="https://example.com/job/1",
        description="Backend development role.",
        location="Bangalore",
        employment_type="Full-time",
        discovered_at=discovered_at,
        created_at=created_at,
    )

    domain_job = to_domain(model)

    assert domain_job == Job(
        id=job_id,
        company="Acme",
        title="Python Developer",
        source="LinkedIn",
        source_url="https://example.com/job/1",
        description="Backend development role.",
        location="Bangalore",
        employment_type="Full-time",
        discovered_at=discovered_at,
        created_at=created_at,
    )


def test_to_model_maps_domain_job() -> None:
    job_id = uuid4()
    discovered_at = datetime.now(UTC)
    created_at = datetime.now(UTC)

    job = Job(
        id=job_id,
        company="Acme",
        title="Python Developer",
        source="LinkedIn",
        source_url="https://example.com/job/1",
        description="Backend development role.",
        location="Bangalore",
        employment_type="Full-time",
        discovered_at=discovered_at,
        created_at=created_at,
    )

    model = to_model(job)

    assert model.id == job.id
    assert model.company == job.company
    assert model.title == job.title
    assert model.source == job.source
    assert model.source_url == job.source_url
    assert model.description == job.description
    assert model.location == job.location
    assert model.employment_type == job.employment_type
    assert model.discovered_at == job.discovered_at
