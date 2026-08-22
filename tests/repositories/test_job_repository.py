from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.job import Job
from packages.database.repositories.job import JobRepository
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


@pytest.mark.asyncio
async def test_create_and_get_job(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    job = Job(
        company="Test Company",
        title="Python Software Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
        description="Python backend engineering role.",
        location="Kerala",
        employment_type="Full-time",
    )

    created = await repository.create(job)
    await session.commit()

    assert created.id is not None
    assert created.company == "Test Company"
    assert created.title == "Python Software Engineer"

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.source_url == created.source_url

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_job_by_source_url(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    source_url = f"https://example.com/jobs/{uuid4()}"

    job = Job(
        company="Source URL Company",
        title="Backend Engineer",
        source="test",
        source_url=source_url,
    )

    await repository.create(job)
    await session.commit()

    fetched = await repository.get_by_source_url(source_url)

    assert fetched is not None
    assert fetched.id == job.id
    assert fetched.company == "Source URL Company"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_nonexistent_job_returns_none(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    job = await repository.get_by_id(uuid4())

    assert job is None


@pytest.mark.asyncio
async def test_get_nonexistent_job_by_source_url_returns_none(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    job = await repository.get_by_source_url(
        f"https://example.com/jobs/{uuid4()}",
    )

    assert job is None


@pytest.mark.asyncio
async def test_duplicate_source_url_raises_integrity_error(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    source_url = f"https://example.com/jobs/{uuid4()}"

    first = Job(
        company="First Company",
        title="First Engineer",
        source="test",
        source_url=source_url,
    )

    second = Job(
        company="Second Company",
        title="Second Engineer",
        source="test",
        source_url=source_url,
    )

    await repository.create(first)
    await session.commit()

    with pytest.raises(IntegrityError):
        await repository.create(second)

    await session.rollback()

    existing = await repository.get_by_source_url(source_url)

    assert existing is not None
    assert existing.id == first.id

    await repository.delete(existing)
    await session.commit()


@pytest.mark.asyncio
async def test_list_all_returns_jobs_in_deterministic_order(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    first = Job(
        company="First Company",
        title="First Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    second = Job(
        company="Second Company",
        title="Second Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    third = Job(
        company="Third Company",
        title="Third Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    await repository.create(first)
    await repository.create(second)
    await repository.create(third)
    await session.commit()

    jobs = await repository.list_all()

    job_ids = {job.id for job in jobs}

    assert first.id in job_ids
    assert second.id in job_ids
    assert third.id in job_ids

    expected = sorted(
        jobs,
        key=lambda job: (job.created_at, job.id),
    )

    assert [job.id for job in jobs] == [job.id for job in expected]

    for job in (first, second, third):
        await repository.delete(job)

    await session.commit()


@pytest.mark.asyncio
async def test_delete_job(
    session: AsyncSession,
) -> None:
    repository = JobRepository(session)

    job = Job(
        company="Delete Test Company",
        title="Delete Test Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    await repository.create(job)
    await session.commit()

    job_id = job.id

    fetched = await repository.get_by_id(job_id)

    assert fetched is not None

    await repository.delete(fetched)
    await session.commit()

    deleted = await repository.get_by_id(job_id)

    assert deleted is None
