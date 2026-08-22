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
from packages.application.resumes.delete_resume import DeleteResume
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
async def test_delete_resume_flow_through_application(
    session: AsyncSession,
) -> None:
    candidate_repository = CandidateRepositoryAdapter(session)
    resume_repository = ResumeRepositoryAdapter(session)

    create_candidate = CreateCandidate(candidate_repository)
    delete_candidate = DeleteCandidate(candidate_repository)
    create_resume = CreateResume(resume_repository)
    get_resume = GetResume(resume_repository)
    delete_resume = DeleteResume(resume_repository)

    candidate = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Delete Resume Integration Candidate",
            email=f"delete-resume-{uuid4()}@example.com",
            phone="1234567890",
            location="Kerala",
        ),
    )

    await session.commit()

    created = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate.id,
            filename="delete-integration.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}-delete-integration.pdf",
        ),
    )

    await session.commit()

    fetched_before_delete = await get_resume.execute(
        GetResumeCommand(
            resume_id=created.id,
        ),
    )

    assert fetched_before_delete is not None
    assert fetched_before_delete.id == created.id

    await delete_resume.execute(created.id)

    await session.commit()

    fetched_after_delete = await get_resume.execute(
        GetResumeCommand(
            resume_id=created.id,
        ),
    )

    assert fetched_after_delete is None

    await delete_candidate.execute(candidate.id)
    await session.commit()
