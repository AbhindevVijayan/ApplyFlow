from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.application import Application
from packages.database.models.candidate import Candidate
from packages.database.models.job import Job
from packages.database.models.resume import Resume
from packages.database.repositories.application_submission_context import (
    DatabaseApplicationSubmissionContextRepository,
)


@pytest.mark.asyncio
async def test_get_submission_context_returns_application_data(
    session: AsyncSession,
    candidate: Candidate,
    job: Job,
    resume: Resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="ready",
    )

    session.add(application)
    await session.flush()

    repository = DatabaseApplicationSubmissionContextRepository(session)

    context = await repository.get_by_application_id(
        application.id,
    )

    assert context is not None

    assert context.application_id == application.id

    assert context.candidate_id == candidate.id
    assert context.candidate_name == "Test Candidate"
    assert context.candidate_email == "test@example.com"
    assert context.candidate_phone == "9876543210"

    assert context.job_id == job.id
    assert context.job_title == "Software Engineer"
    assert context.company == "Test Company"
    assert context.source == "test"
    assert context.source_url.startswith(
        "https://example.com/jobs/test-software-engineer-",
    )

    assert context.resume_id == resume.id
    assert context.resume_filename == "resume.pdf"
    assert context.resume_storage_key == (f"test-resumes/{candidate.id}/resume.pdf")


@pytest.mark.asyncio
async def test_get_submission_context_returns_none_for_unknown_application(
    session: AsyncSession,
) -> None:
    repository = DatabaseApplicationSubmissionContextRepository(session)

    context = await repository.get_by_application_id(uuid4())

    assert context is None
