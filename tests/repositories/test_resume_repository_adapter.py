from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.database.repositories.resume_adapter import (
    ResumeRepositoryAdapter,
)
from packages.database.session import SessionFactory
from packages.domain.candidates.entities import Candidate
from packages.domain.resumes.entities import Resume


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def candidate(session: AsyncSession) -> Candidate:
    repository = CandidateRepositoryAdapter(session)

    created = await repository.create(
        Candidate(
            id=uuid4(),
            full_name="Resume Test Candidate",
            email=f"resume-test-{uuid4()}@example.com",
        ),
    )

    await session.commit()

    return created


@pytest.mark.asyncio
async def test_adapter_creates_and_returns_domain_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepositoryAdapter(session)

    resume = Resume(
        id=uuid4(),
        candidate_id=candidate.id,
        filename="adapter-resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
        parsed_text="Python backend developer.",
        is_canonical=True,
    )

    created = await repository.create(resume)
    await session.commit()

    assert created.id == resume.id
    assert isinstance(created, Resume)
    assert created.filename == "adapter-resume.pdf"
    assert created.parsed_text == "Python backend developer."
    assert created.is_canonical is True

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert isinstance(fetched, Resume)
    assert fetched.id == created.id

    await repository.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_candidate_id_returns_domain_resumes(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepositoryAdapter(session)

    first = await repository.create(
        Resume(
            id=uuid4(),
            candidate_id=candidate.id,
            filename="first.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}.pdf",
        ),
    )

    second = await repository.create(
        Resume(
            id=uuid4(),
            candidate_id=candidate.id,
            filename="second.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}.pdf",
        ),
    )

    await session.commit()

    resumes = await repository.get_by_candidate_id(candidate.id)

    ids = {resume.id for resume in resumes}

    assert first.id in ids
    assert second.id in ids
    assert all(isinstance(resume, Resume) for resume in resumes)

    await repository.delete(first.id)
    await repository.delete(second.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_canonical_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepositoryAdapter(session)

    resume = await repository.create(
        Resume(
            id=uuid4(),
            candidate_id=candidate.id,
            filename="canonical.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}.pdf",
            is_canonical=True,
        ),
    )

    await session.commit()

    canonical = await repository.get_canonical_by_candidate_id(
        candidate.id,
    )

    assert canonical is not None
    assert isinstance(canonical, Resume)
    assert canonical.id == resume.id
    assert canonical.is_canonical is True

    await repository.delete(resume.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_delete_removes_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepositoryAdapter(session)

    resume = await repository.create(
        Resume(
            id=uuid4(),
            candidate_id=candidate.id,
            filename="delete.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}.pdf",
        ),
    )

    await session.commit()

    await repository.delete(resume.id)
    await session.commit()

    deleted = await repository.get_by_id(resume.id)

    assert deleted is None
