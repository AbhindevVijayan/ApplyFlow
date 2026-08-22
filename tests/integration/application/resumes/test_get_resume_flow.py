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
from packages.application.resumes.get_resume import (
    GetResume,
    GetResumeCommand,
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
async def test_get_resume_flow_through_application(
    session: AsyncSession,
) -> None:
    candidate_repository = CandidateRepositoryAdapter(session)
    resume_repository = ResumeRepositoryAdapter(session)

    create_candidate = CreateCandidate(candidate_repository)
    delete_candidate = DeleteCandidate(candidate_repository)
    create_resume = CreateResume(resume_repository)
    get_resume = GetResume(resume_repository)

    candidate = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Get Resume Integration Candidate",
            email=f"get-resume-{uuid4()}@example.com",
            phone="1234567890",
            location="Kerala",
        ),
    )

    await session.commit()

    created = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate.id,
            filename="integration-resume.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}-integration-resume.pdf",
            is_canonical=True,
        ),
    )

    await session.commit()

    fetched = await get_resume.execute(
        GetResumeCommand(
            resume_id=created.id,
        ),
    )

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.candidate_id == candidate.id
    assert fetched.filename == "integration-resume.pdf"
    assert fetched.content_type == "application/pdf"
    assert fetched.storage_key == created.storage_key
    assert fetched.is_canonical is True

    await delete_candidate.execute(candidate.id)
    await session.commit()
