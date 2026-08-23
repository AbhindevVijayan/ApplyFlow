from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from packages.database.models.application import Application
from packages.database.repositories.application import ApplicationRepository


@pytest.mark.asyncio
async def test_create_application(
    session,
    candidate,
    job,
    resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    repository = ApplicationRepository(session)

    created = await repository.create(application)

    assert created.id is not None
    assert created.candidate_id == candidate.id
    assert created.job_id == job.id
    assert created.resume_id == resume.id
    assert created.status == "draft"


@pytest.mark.asyncio
async def test_get_by_id(
    session,
    candidate,
    job,
    resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="ready",
    )

    repository = ApplicationRepository(session)

    created = await repository.create(application)

    result = await repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.status == "ready"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(session) -> None:
    repository = ApplicationRepository(session)

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_candidate_id(
    session,
    candidate,
    job,
    resume,
) -> None:
    second_job = type(job)(
        company="Second Company",
        title="Second Job",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    session.add(second_job)
    await session.flush()

    first = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    second = Application(
        candidate_id=candidate.id,
        job_id=second_job.id,
        resume_id=resume.id,
        status="submitted",
    )

    repository = ApplicationRepository(session)

    await repository.create(first)
    await repository.create(second)

    results = await repository.get_by_candidate_id(candidate.id)

    assert len(results) == 2
    assert {application.id for application in results} == {
        first.id,
        second.id,
    }


@pytest.mark.asyncio
async def test_get_by_job_id(
    session,
    candidate,
    job,
    resume,
) -> None:
    second_candidate = type(candidate)(
        full_name="Second Candidate",
        email=f"second-{uuid4()}@example.com",
    )

    session.add(second_candidate)
    await session.flush()

    first = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    second_resume = type(resume)(
        candidate_id=second_candidate.id,
        filename="second-resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    session.add(second_resume)
    await session.flush()

    second = Application(
        candidate_id=second_candidate.id,
        job_id=job.id,
        resume_id=second_resume.id,
        status="submitted",
    )

    repository = ApplicationRepository(session)

    await repository.create(first)
    await repository.create(second)

    results = await repository.get_by_job_id(job.id)

    assert len(results) == 2
    assert {application.id for application in results} == {
        first.id,
        second.id,
    }


@pytest.mark.asyncio
async def test_get_by_candidate_and_job(
    session,
    candidate,
    job,
    resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="submitted",
    )

    repository = ApplicationRepository(session)

    await repository.create(application)

    result = await repository.get_by_candidate_and_job(
        candidate.id,
        job.id,
    )

    assert result is not None
    assert result.id == application.id


@pytest.mark.asyncio
async def test_get_by_candidate_and_job_returns_none_when_missing(
    session,
) -> None:
    repository = ApplicationRepository(session)

    result = await repository.get_by_candidate_and_job(
        uuid4(),
        uuid4(),
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_application(
    session,
    candidate,
    job,
    resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
        notes="Initial notes",
    )

    repository = ApplicationRepository(session)

    created = await repository.create(application)

    created.status = "submitted"
    created.notes = "Application submitted."

    updated = await repository.update(created)

    assert updated.id == created.id
    assert updated.status == "submitted"
    assert updated.notes == "Application submitted."


@pytest.mark.asyncio
async def test_update_missing_application_raises(
    session,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepository(session)

    application = Application(
        id=uuid4(),
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    with pytest.raises(ValueError, match="Application not found"):
        await repository.update(application)


@pytest.mark.asyncio
async def test_delete_application(
    session,
    candidate,
    job,
    resume,
) -> None:
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    repository = ApplicationRepository(session)

    created = await repository.create(application)

    await repository.delete(created)

    result = await repository.get_by_id(created.id)

    assert result is None


@pytest.mark.asyncio
async def test_duplicate_candidate_job_is_rejected(
    session,
    candidate,
    job,
    resume,
) -> None:
    first = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    second = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status="draft",
    )

    repository = ApplicationRepository(session)

    await repository.create(first)

    with pytest.raises(IntegrityError):
        await repository.create(second)
