from datetime import datetime
from uuid import uuid4

from packages.domain.jobs.entities import Job


def test_job_is_immutable() -> None:
    job = Job(
        id=uuid4(),
        company="Acme",
        title="Python Developer",
        source="linkedin",
        source_url="https://example.com/jobs/123",
    )

    try:
        job.title = "Senior Python Developer"
    except AttributeError:
        pass
    else:
        raise AssertionError("Job should be immutable")


def test_job_supports_optional_fields() -> None:
    job = Job(
        id=uuid4(),
        company="Acme",
        title="Python Developer",
        source="linkedin",
        source_url="https://example.com/jobs/123",
    )

    assert job.description is None
    assert job.location is None
    assert job.employment_type is None
    assert job.discovered_at is None
    assert job.created_at is None


def test_job_contains_all_fields() -> None:
    discovered_at = datetime.now()
    created_at = datetime.now()

    job = Job(
        id=uuid4(),
        company="Acme",
        title="Python Developer",
        source="linkedin",
        source_url="https://example.com/jobs/123",
        description="Build backend services.",
        location="Bangalore",
        employment_type="full-time",
        discovered_at=discovered_at,
        created_at=created_at,
    )

    assert job.company == "Acme"
    assert job.title == "Python Developer"
    assert job.source == "linkedin"
    assert job.source_url == "https://example.com/jobs/123"
    assert job.description == "Build backend services."
    assert job.location == "Bangalore"
    assert job.employment_type == "full-time"
    assert job.discovered_at == discovered_at
    assert job.created_at == created_at
