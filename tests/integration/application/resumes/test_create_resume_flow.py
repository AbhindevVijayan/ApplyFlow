from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.candidates.create_candidate import (
    CreateCandidate,
    CreateCandidateCommand,
)
from packages.application.candidates.delete_candidate import DeleteCandidate
from packages.application.resumes.create_resume import (
    CreateResume,
    CreateResumeCommand,
)
from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.database.repositories.resume_adapter import (
    ResumeRepositoryAdapter,
)
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.mark.asyncio
async def test_create_canonical_resume_replaces_existing_canonical(
    session: AsyncSession,
) -> None:
    candidate_repository = CandidateRepositoryAdapter(session)
    resume_repository = ResumeRepositoryAdapter(session)

    create_candidate = CreateCandidate(candidate_repository)
    delete_candidate = DeleteCandidate(candidate_repository)
    create_resume = CreateResume(resume_repository)

    candidate = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Resume Integration Candidate",
            email=f"resume-integration-{uuid4()}@example.com",
            phone="1234567890",
            location="Kerala",
        ),
    )

    await session.commit()

    first = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate.id,
            filename="first.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}-first.pdf",
            is_canonical=True,
        ),
    )

    await session.commit()

    second = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate.id,
            filename="second.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}-second.pdf",
            is_canonical=True,
        ),
    )

    await session.commit()

    stored_first = await resume_repository.get_by_id(first.id)
    stored_second = await resume_repository.get_by_id(second.id)

    assert stored_first is not None
    assert stored_second is not None

    assert stored_first.is_canonical is False
    assert stored_second.is_canonical is True

    canonical = await resume_repository.get_canonical_by_candidate_id(
        candidate.id,
    )

    assert canonical is not None
    assert canonical.id == second.id

    await delete_candidate.execute(candidate.id)
    await session.commit()
