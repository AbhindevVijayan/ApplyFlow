from datetime import UTC, datetime
from uuid import UUID

import pytest

from packages.application.jobs.update_job import (
    JobNotFoundError,
    JobSourceURLAlreadyExistsError,
    UpdateJob,
    UpdateJobCommand,
)
from packages.domain.jobs.entities import Job


class FakeJobRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.jobs: list[Job] = []
        self.updated_job: Job | None = None

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
        self.updated_job = job

        self.jobs = [job if existing.id == job.id else existing for existing in self.jobs]

        return job

    async def delete(self, job_id: UUID) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]


def make_job(
    *,
    job_id: UUID | None = None,
    source_url: str = "https://example.com/jobs/1",
) -> Job:
    return Job(
        id=job_id or UUID("11111111-1111-1111-1111-111111111111"),
        company="Acme Technologies",
        title="Software Engineer",
        source="LinkedIn",
        source_url=source_url,
        description="Backend engineering role.",
        location="Kerala",
        employment_type="Full-time",
        discovered_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        created_at=datetime(
            2026,
            1,
            2,
            tzinfo=UTC,
        ),
    )


@pytest.mark.asyncio
async def test_update_job_updates_supplied_fields() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    updated = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            company="Updated Technologies",
            title="Senior Software Engineer",
            location="Bangalore",
        ),
    )

    assert updated.company == "Updated Technologies"
    assert updated.title == "Senior Software Engineer"
    assert updated.location == "Bangalore"


@pytest.mark.asyncio
async def test_update_job_preserves_unspecified_fields() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    updated = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            title="Senior Software Engineer",
        ),
    )

    assert updated.company == job.company
    assert updated.title == "Senior Software Engineer"
    assert updated.source == job.source
    assert updated.source_url == job.source_url
    assert updated.description == job.description
    assert updated.location == job.location
    assert updated.employment_type == job.employment_type
    assert updated.discovered_at == job.discovered_at


@pytest.mark.asyncio
async def test_update_job_can_clear_nullable_fields() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    updated = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            description=None,
            location=None,
            employment_type=None,
            discovered_at=None,
        ),
    )

    assert updated.description is None
    assert updated.location is None
    assert updated.employment_type is None
    assert updated.discovered_at is None


@pytest.mark.asyncio
async def test_update_job_rejects_unknown_job() -> None:
    repository = FakeJobRepository()

    use_case = UpdateJob(repository)

    job_id = UUID(
        "22222222-2222-2222-2222-222222222222",
    )

    with pytest.raises(
        JobNotFoundError,
        match=f"Job '{job_id}' was not found.",
    ):
        await use_case.execute(
            UpdateJobCommand(
                job_id=job_id,
                title="Updated Title",
            ),
        )

    assert repository.jobs == []


@pytest.mark.asyncio
async def test_update_job_rejects_duplicate_source_url() -> None:
    repository = FakeJobRepository()

    first_job = make_job()

    second_job = make_job(
        job_id=UUID(
            "22222222-2222-2222-2222-222222222222",
        ),
        source_url="https://example.com/jobs/2",
    )

    await repository.create(first_job)
    await repository.create(second_job)

    use_case = UpdateJob(repository)

    with pytest.raises(
        JobSourceURLAlreadyExistsError,
        match="already exists",
    ):
        await use_case.execute(
            UpdateJobCommand(
                job_id=second_job.id,
                source_url=first_job.source_url,
            ),
        )

    assert repository.updated_job is None


@pytest.mark.asyncio
async def test_update_job_allows_existing_source_url() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    updated = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            source_url=job.source_url,
            title="Updated Title",
        ),
    )

    assert updated.source_url == job.source_url
    assert updated.title == "Updated Title"


@pytest.mark.asyncio
async def test_update_job_preserves_created_at() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    updated = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            title="Updated Title",
        ),
    )

    assert updated.created_at == job.created_at


@pytest.mark.asyncio
async def test_update_job_does_not_mutate_original_job() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    original = job

    use_case = UpdateJob(repository)

    await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            title="Updated Title",
        ),
    )

    assert original.title == "Software Engineer"
    assert original.company == "Acme Technologies"


@pytest.mark.asyncio
async def test_update_job_returns_persisted_job() -> None:
    repository = FakeJobRepository()

    job = make_job()
    await repository.create(job)

    use_case = UpdateJob(repository)

    result = await use_case.execute(
        UpdateJobCommand(
            job_id=job.id,
            title="Updated Title",
        ),
    )

    assert result is repository.updated_job
    assert result.title == "Updated Title"
