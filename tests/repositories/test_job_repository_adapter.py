from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.repositories.job_adapter import JobRepositoryAdapter
from packages.database.session import SessionFactory
from packages.domain.jobs.entities import Job


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


def make_job(
    *,
    source_url: str | None = None,
) -> Job:
    return Job(
        id=uuid4(),
        company="Adapter Test Company",
        title="Python Software Engineer",
        source="test",
        source_url=source_url or f"https://example.com/jobs/{uuid4()}",
        description="Python and FastAPI role.",
        location="Kerala",
        employment_type="Full-time",
    )


@pytest.mark.asyncio
async def test_adapter_creates_and_returns_domain_job(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)
    job = make_job()

    created = await repository.create(job)
    await session.commit()

    assert isinstance(created, Job)
    assert created.id == job.id
    assert created.company == job.company
    assert created.title == job.title
    assert created.source_url == job.source_url

    await repository.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_id_returns_domain_job(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)
    job = make_job()

    await repository.create(job)
    await session.commit()

    fetched = await repository.get_by_id(job.id)

    assert fetched is not None
    assert isinstance(fetched, Job)
    assert fetched.id == job.id
    assert fetched.company == job.company

    await repository.delete(job.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_source_url_returns_domain_job(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)
    job = make_job(
        source_url="https://example.com/adapter-source-url",
    )

    await repository.create(job)
    await session.commit()

    fetched = await repository.get_by_source_url(job.source_url)

    assert fetched is not None
    assert isinstance(fetched, Job)
    assert fetched.id == job.id

    await repository.delete(job.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_returns_none_for_unknown_job(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_adapter_returns_none_for_unknown_source_url(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)

    result = await repository.get_by_source_url(
        "https://example.com/does-not-exist",
    )

    assert result is None


@pytest.mark.asyncio
async def test_adapter_list_all_returns_domain_jobs(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)

    first = make_job()
    second = make_job()

    await repository.create(first)
    await repository.create(second)
    await session.commit()

    jobs = await repository.list_all()

    job_ids = {job.id for job in jobs}

    assert first.id in job_ids
    assert second.id in job_ids
    assert all(isinstance(job, Job) for job in jobs)

    await repository.delete(first.id)
    await repository.delete(second.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_delete_removes_job(
    session: AsyncSession,
) -> None:
    repository = JobRepositoryAdapter(session)
    job = make_job()

    await repository.create(job)
    await session.commit()

    await repository.delete(job.id)
    await session.commit()

    result = await repository.get_by_id(job.id)

    assert result is None
