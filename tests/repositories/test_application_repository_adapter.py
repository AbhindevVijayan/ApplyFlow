from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.models.job import Job
from packages.database.models.resume import Resume
from packages.database.repositories.application_adapter import (
    ApplicationRepositoryAdapter,
)
from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)


def make_application(
    *,
    candidate_id,
    job_id,
    resume_id,
    status: ApplicationStatus = ApplicationStatus.DRAFT,
) -> Application:
    return Application(
        id=uuid4(),
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


async def create_second_candidate(
    session: AsyncSession,
) -> Candidate:
    candidate = Candidate(
        full_name="Second Test Candidate",
        email=f"second-{uuid4()}@example.com",
        phone="9876543211",
        location="Kerala",
    )

    session.add(candidate)
    await session.flush()

    return candidate


async def create_second_job(
    session: AsyncSession,
) -> Job:
    job = Job(
        company="Second Test Company",
        title="Backend Engineer",
        source="test",
        source_url=(f"https://example.com/jobs/second-backend-engineer-{uuid4()}"),
        description="Second test job description",
        location="Bangalore",
        employment_type="Full-time",
    )

    session.add(job)
    await session.flush()

    return job


async def create_resume_for_candidate(
    session: AsyncSession,
    candidate: Candidate,
) -> Resume:
    resume = Resume(
        candidate_id=candidate.id,
        filename="second-resume.pdf",
        content_type="application/pdf",
        storage_key=(f"test-resumes/{candidate.id}/second-resume.pdf"),
        parsed_text="Second test resume content",
        is_canonical=True,
    )

    session.add(resume)
    await session.flush()

    return resume


async def test_adapter_creates_and_returns_domain_application(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    application = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    created = await repository.create(application)
    await session.flush()

    assert isinstance(created, Application)
    assert created.id == application.id
    assert created.candidate_id == application.candidate_id
    assert created.job_id == application.job_id
    assert created.resume_id == application.resume_id
    assert created.status == application.status

    await repository.delete(created.id)
    await session.flush()


async def test_adapter_get_by_id_returns_domain_application(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    application = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    await repository.create(application)
    await session.flush()

    fetched = await repository.get_by_id(application.id)

    assert fetched is not None
    assert isinstance(fetched, Application)
    assert fetched.id == application.id
    assert fetched.candidate_id == application.candidate_id
    assert fetched.job_id == application.job_id

    await repository.delete(application.id)
    await session.flush()


@pytest.mark.asyncio
async def test_adapter_returns_none_for_unknown_application(
    session: AsyncSession,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    result = await repository.get_by_id(uuid4())

    assert result is None


async def test_adapter_get_by_candidate_id_returns_domain_applications(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    second_job = await create_second_job(session)

    first = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    second = make_application(
        candidate_id=candidate.id,
        job_id=second_job.id,
        resume_id=resume.id,
    )

    await repository.create(first)
    await repository.create(second)
    await session.flush()

    applications = await repository.get_by_candidate_id(
        candidate.id,
    )

    application_ids = {application.id for application in applications}

    assert first.id in application_ids
    assert second.id in application_ids
    assert all(isinstance(application, Application) for application in applications)

    await repository.delete(first.id)
    await repository.delete(second.id)
    await session.flush()


async def test_adapter_get_by_job_id_returns_domain_applications(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    second_candidate = await create_second_candidate(session)
    second_resume = await create_resume_for_candidate(
        session,
        second_candidate,
    )

    first = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    second = make_application(
        candidate_id=second_candidate.id,
        job_id=job.id,
        resume_id=second_resume.id,
    )

    await repository.create(first)
    await repository.create(second)
    await session.flush()

    applications = await repository.get_by_job_id(job.id)

    application_ids = {application.id for application in applications}

    assert first.id in application_ids
    assert second.id in application_ids
    assert all(isinstance(application, Application) for application in applications)

    await repository.delete(first.id)
    await repository.delete(second.id)
    await session.flush()


async def test_adapter_get_by_candidate_and_job_returns_domain_application(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    application = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    await repository.create(application)
    await session.flush()

    fetched = await repository.get_by_candidate_and_job(
        candidate.id,
        job.id,
    )

    assert fetched is not None
    assert isinstance(fetched, Application)
    assert fetched.id == application.id

    await repository.delete(application.id)
    await session.flush()


@pytest.mark.asyncio
async def test_adapter_update_persists_domain_application_changes(
    session: AsyncSession,
    candidate,
    job,
    resume,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    application = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status=ApplicationStatus.READY,
    )

    await repository.create(application)
    await session.flush()

    updated_application = replace(
        application,
        status=ApplicationStatus.SUBMITTED,
        external_application_url=("https://example.com/application/123"),
    )

    updated = await repository.update(updated_application)
    await session.flush()

    assert isinstance(updated, Application)
    assert updated.id == application.id
    assert updated.status == ApplicationStatus.SUBMITTED
    assert updated.external_application_url == "https://example.com/application/123"

    fetched = await repository.get_by_id(application.id)

    assert fetched is not None
    assert fetched.status == ApplicationStatus.SUBMITTED
    assert fetched.external_application_url == "https://example.com/application/123"

    await repository.delete(application.id)
    await session.flush()


@pytest.mark.asyncio
async def test_adapter_delete_removes_application(
    candidate,
    job,
    resume,
    session: AsyncSession,
) -> None:
    repository = ApplicationRepositoryAdapter(session)

    application = make_application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
    )

    await repository.create(application)
    await session.flush()

    await repository.delete(application.id)
    await session.flush()

    result = await repository.get_by_id(application.id)

    assert result is None
