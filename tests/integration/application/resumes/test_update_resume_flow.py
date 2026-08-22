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
from packages.application.resumes.update_resume import (
    UpdateResume,
    UpdateResumeCommand,
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
async def test_update_resume_flow_through_application(
    session: AsyncSession,
) -> None:
    candidate_repository = CandidateRepositoryAdapter(session)
    resume_repository = ResumeRepositoryAdapter(session)

    create_candidate = CreateCandidate(candidate_repository)
    delete_candidate = DeleteCandidate(candidate_repository)
    create_resume = CreateResume(resume_repository)
    get_resume = GetResume(resume_repository)
    update_resume = UpdateResume(resume_repository)

    candidate = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Update Resume Integration Candidate",
            email=f"update-resume-{uuid4()}@example.com",
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
            parsed_text="First resume",
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
            parsed_text="Second resume",
        ),
    )

    await session.commit()

    updated = await update_resume.execute(
        UpdateResumeCommand(
            resume_id=second.id,
            filename="second-updated.pdf",
            content_type="application/pdf",
            storage_key=f"resumes/{uuid4()}-second-updated.pdf",
            parsed_text="Updated resume",
            is_canonical=True,
        ),
    )

    await session.commit()

    assert updated.id == second.id
    assert updated.candidate_id == candidate.id
    assert updated.filename == "second-updated.pdf"
    assert updated.parsed_text == "Updated resume"
    assert updated.is_canonical is True

    fetched_first = await get_resume.execute(
        GetResumeCommand(
            resume_id=first.id,
        ),
    )

    fetched_second = await get_resume.execute(
        GetResumeCommand(
            resume_id=second.id,
        ),
    )

    assert fetched_first is not None
    assert fetched_second is not None

    assert fetched_first.is_canonical is False
    assert fetched_second.is_canonical is True
    assert fetched_second.filename == "second-updated.pdf"
    assert fetched_second.parsed_text == "Updated resume"

    await delete_candidate.execute(candidate.id)
    await session.commit()
