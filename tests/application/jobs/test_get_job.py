from uuid import UUID, uuid4

import pytest

from packages.application.jobs.get_job import (
    GetJob,
    JobNotFoundError,
)
from packages.domain.jobs.entities import Job


class FakeJobRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.jobs: dict[UUID, Job] = {}

    async def create(self, job: Job) -> Job:
        self.jobs[job.id] = job
        return job

    async def get_by_id(
        self,
        job_id: UUID,
    ) -> Job | None:
        return self.jobs.get(job_id)

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        for job in self.jobs.values():
            if job.source_url == source_url:
                return job

        return None

    async def list_all(self) -> list[Job]:
        return list(self.jobs.values())

    async def update(self, job: Job) -> Job:
        if job.id not in self.jobs:
            raise ValueError(f"Job not found: {job.id}")

        self.jobs[job.id] = job
        return job

    async def delete(
        self,
        job_id: UUID,
    ) -> None:
        self.jobs.pop(job_id, None)


@pytest.mark.asyncio
async def test_get_job_returns_existing_job() -> None:
    repository = FakeJobRepository()

    job = Job(
        id=uuid4(),
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url="https://example.com/jobs/123",
        description="Backend engineering role.",
        location="Bangalore",
        employment_type="Full-time",
    )

    await repository.create(job)

    use_case = GetJob(repository)

    result = await use_case.execute(job.id)

    assert result is job
    assert result.id == job.id
    assert result.company == "Acme Technologies"
    assert result.title == "Software Engineer"
    assert result.source == "LinkedIn"


@pytest.mark.asyncio
async def test_get_job_rejects_unknown_job() -> None:
    repository = FakeJobRepository()

    use_case = GetJob(repository)

    job_id = uuid4()

    with pytest.raises(JobNotFoundError):
        await use_case.execute(job_id)


@pytest.mark.asyncio
async def test_get_job_does_not_modify_repository() -> None:
    repository = FakeJobRepository()

    job = Job(
        id=uuid4(),
        company="Read Only Company",
        title="Python Developer",
        source="Company Website",
        source_url="https://example.com/jobs/456",
    )

    await repository.create(job)

    use_case = GetJob(repository)

    result = await use_case.execute(job.id)

    assert result == job
    assert len(repository.jobs) == 1
    assert repository.jobs[job.id] == job
