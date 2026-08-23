from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from packages.database.models.candidate import Candidate
from packages.database.models.job import Job
from packages.database.models.resume import Resume
from packages.database.session import engine


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

        await transaction.rollback()


@pytest.fixture
async def candidate(session: AsyncSession) -> Candidate:
    candidate = Candidate(
        full_name="Test Candidate",
        email="test@example.com",
        phone="9876543210",
        location="Kerala",
    )

    session.add(candidate)
    await session.flush()

    return candidate


@pytest.fixture
async def job(session: AsyncSession) -> Job:
    job = Job(
        company="Test Company",
        title="Software Engineer",
        source="test",
        source_url="https://example.com/jobs/test-software-engineer",
        description="Test job description",
        location="Bangalore",
        employment_type="Full-time",
    )

    session.add(job)
    await session.flush()

    return job


@pytest.fixture
async def resume(
    session: AsyncSession,
    candidate: Candidate,
) -> Resume:
    resume = Resume(
        candidate_id=candidate.id,
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key=f"test-resumes/{candidate.id}/resume.pdf",
        parsed_text="Test resume content",
        is_canonical=True,
    )

    session.add(resume)
    await session.flush()

    return resume
