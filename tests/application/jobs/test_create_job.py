from datetime import UTC, datetime
from uuid import UUID

import pytest

from packages.application.jobs.create_job import (
    CreateJob,
    CreateJobCommand,
    JobAlreadyExistsError,
)
from packages.domain.jobs.entities import Job


class FakeJobRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.jobs: list[Job] = []

    async def create(self, job: Job) -> Job:
        self.jobs.append(job)
        return job

    async def get_by_id(self, job_id: UUID) -> Job | None:
        return next(
            (job for job in self.jobs if job.id == job_id),
            None,
        )

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        return next(
            (job for job in self.jobs if job.source_url == source_url),
            None,
        )

    async def list_all(self) -> list[Job]:
        return list(self.jobs)

    async def delete(self, job_id: UUID) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]

    async def update(self, job: Job) -> Job:
        self.jobs = [job if existing.id == job.id else existing for existing in self.jobs]
        return job


@pytest.mark.asyncio
async def test_create_job_creates_and_returns_job() -> None:
    repository = FakeJobRepository()
    use_case = CreateJob(repository)

    discovered_at = datetime(
        2026,
        8,
        21,
        10,
        30,
        tzinfo=UTC,
    )

    command = CreateJobCommand(
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url="https://example.com/jobs/123",
        description="Backend software engineering role.",
        location="Bangalore",
        employment_type="Full-time",
        discovered_at=discovered_at,
    )

    job = await use_case.execute(command)

    assert job.company == "Acme Technologies"
    assert job.title == "Software Engineer"
    assert job.source == "LinkedIn"
    assert job.source_url == "https://example.com/jobs/123"
    assert job.description == "Backend software engineering role."
    assert job.location == "Bangalore"
    assert job.employment_type == "Full-time"
    assert job.discovered_at == discovered_at

    assert job.id is not None
    assert isinstance(job.id, UUID)

    assert repository.jobs == [job]


@pytest.mark.asyncio
async def test_create_job_allows_optional_fields_to_be_none() -> None:
    repository = FakeJobRepository()
    use_case = CreateJob(repository)

    command = CreateJobCommand(
        company="Acme Technologies",
        title="Python Developer",
        source="Company Website",
        source_url="https://example.com/jobs/456",
    )

    job = await use_case.execute(command)

    assert job.company == "Acme Technologies"
    assert job.title == "Python Developer"
    assert job.source == "Company Website"
    assert job.source_url == "https://example.com/jobs/456"

    assert job.description is None
    assert job.location is None
    assert job.employment_type is None
    assert job.discovered_at is None


@pytest.mark.asyncio
async def test_create_job_rejects_duplicate_source_url() -> None:
    repository = FakeJobRepository()

    existing = Job(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        company="Existing Company",
        title="Existing Job",
        source="LinkedIn",
        source_url="https://example.com/jobs/duplicate",
    )

    repository.jobs.append(existing)

    use_case = CreateJob(repository)

    command = CreateJobCommand(
        company="Another Company",
        title="Another Job",
        source="Indeed",
        source_url="https://example.com/jobs/duplicate",
    )

    with pytest.raises(
        JobAlreadyExistsError,
        match="Job with source URL 'https://example.com/jobs/duplicate' already exists.",
    ):
        await use_case.execute(command)

    assert repository.jobs == [existing]
