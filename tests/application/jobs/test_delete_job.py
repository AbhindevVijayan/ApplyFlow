from uuid import UUID

import pytest

from packages.application.jobs.delete_job import (
    DeleteJob,
    JobNotFoundError,
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

    async def update(self, job: Job) -> Job:
        for index, existing_job in enumerate(self.jobs):
            if existing_job.id == job.id:
                self.jobs[index] = job
                return job

        raise ValueError(f"Job not found: {job.id}")

    async def delete(self, job_id: UUID) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]


@pytest.mark.asyncio
async def test_delete_job_removes_existing_job() -> None:
    repository = FakeJobRepository()

    job = Job(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url="https://example.com/jobs/1",
    )

    await repository.create(job)

    use_case = DeleteJob(repository)

    await use_case.execute(job.id)

    assert repository.jobs == []


@pytest.mark.asyncio
async def test_delete_job_rejects_unknown_job() -> None:
    repository = FakeJobRepository()

    use_case = DeleteJob(repository)

    job_id = UUID("22222222-2222-2222-2222-222222222222")

    with pytest.raises(
        JobNotFoundError,
        match=f"Job '{job_id}' was not found.",
    ):
        await use_case.execute(job_id)

    assert repository.jobs == []


@pytest.mark.asyncio
async def test_delete_job_only_deletes_requested_job() -> None:
    repository = FakeJobRepository()

    first_job = Job(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url="https://example.com/jobs/1",
    )

    second_job = Job(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        company="Example Systems",
        title="Python Developer",
        source="Indeed",
        source_url="https://example.com/jobs/2",
    )

    await repository.create(first_job)
    await repository.create(second_job)

    use_case = DeleteJob(repository)

    await use_case.execute(first_job.id)

    assert repository.jobs == [second_job]
