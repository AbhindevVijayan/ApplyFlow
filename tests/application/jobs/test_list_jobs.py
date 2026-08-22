from uuid import uuid4

import pytest

from packages.application.jobs.list_jobs import ListJobs
from packages.domain.jobs.entities import Job


class FakeJobRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.jobs: list[Job] = []

    async def create(self, job: Job) -> Job:
        self.jobs.append(job)
        return job

    async def get_by_id(self, job_id):
        return next(
            (job for job in self.jobs if job.id == job_id),
            None,
        )

    async def get_by_source_url(self, source_url: str):
        return next(
            (job for job in self.jobs if job.source_url == source_url),
            None,
        )

    async def list_all(self) -> list[Job]:
        return list(self.jobs)

    async def delete(self, job_id) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]


@pytest.mark.asyncio
async def test_list_jobs_returns_all_jobs() -> None:
    repository = FakeJobRepository()

    first_job = Job(
        id=uuid4(),
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url="https://example.com/jobs/1",
    )

    second_job = Job(
        id=uuid4(),
        company="Example Systems",
        title="Python Developer",
        source="Indeed",
        source_url="https://example.com/jobs/2",
    )

    await repository.create(first_job)
    await repository.create(second_job)

    use_case = ListJobs(repository)

    result = await use_case.execute()

    assert result == [first_job, second_job]


@pytest.mark.asyncio
async def test_list_jobs_returns_empty_sequence_when_no_jobs_exist() -> None:
    repository = FakeJobRepository()

    use_case = ListJobs(repository)

    result = await use_case.execute()

    assert result == []


@pytest.mark.asyncio
async def test_list_jobs_does_not_modify_repository() -> None:
    repository = FakeJobRepository()

    job = Job(
        id=uuid4(),
        company="Acme Technologies",
        title="Backend Engineer",
        source="Company Website",
        source_url="https://example.com/jobs/3",
    )

    await repository.create(job)

    use_case = ListJobs(repository)

    result = await use_case.execute()

    assert result == [job]
    assert repository.jobs == [job]
