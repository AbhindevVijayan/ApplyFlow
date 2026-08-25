from uuid import uuid4

import pytest

from packages.application.applications.create_application import (
    ApplicationAlreadyExistsError,
    CreateApplication,
    CreateApplicationCommand,
)
from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)


class FakeApplicationRepository:
    def __init__(
        self,
        existing: Application | None = None,
    ) -> None:
        self.existing = existing
        self.created: list[Application] = []

    async def get_by_candidate_and_job(
        self,
        candidate_id,
        job_id,
    ):
        if self.existing is None:
            return None

        if self.existing.candidate_id == candidate_id and self.existing.job_id == job_id:
            return self.existing

        return None

    async def create(
        self,
        application: Application,
    ) -> Application:
        self.created.append(application)
        return application


@pytest.mark.asyncio
async def test_create_application_creates_draft_application() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    resume_id = uuid4()

    repository = FakeApplicationRepository()
    use_case = CreateApplication(repository)

    result = await use_case.execute(
        CreateApplicationCommand(
            candidate_id=candidate_id,
            job_id=job_id,
            resume_id=resume_id,
        ),
    )

    assert result.id is not None
    assert result.candidate_id == candidate_id
    assert result.job_id == job_id
    assert result.resume_id == resume_id
    assert result.status == ApplicationStatus.DRAFT

    assert len(repository.created) == 1
    assert repository.created[0] == result


@pytest.mark.asyncio
async def test_create_application_preserves_command_fields() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    resume_id = uuid4()

    repository = FakeApplicationRepository()
    use_case = CreateApplication(repository)

    command = CreateApplicationCommand(
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status=ApplicationStatus.READY,
        external_application_url="https://example.com/apply",
        notes="Tailored resume selected.",
        failure_reason=None,
    )

    result = await use_case.execute(command)

    assert result.status == ApplicationStatus.READY
    assert result.external_application_url == ("https://example.com/apply")
    assert result.notes == "Tailored resume selected."
    assert result.failure_reason is None


@pytest.mark.asyncio
async def test_create_application_rejects_duplicate_candidate_job() -> None:
    candidate_id = uuid4()
    job_id = uuid4()

    existing = Application(
        id=uuid4(),
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=uuid4(),
        status=ApplicationStatus.DRAFT,
    )

    repository = FakeApplicationRepository(existing=existing)
    use_case = CreateApplication(repository)

    with pytest.raises(
        ApplicationAlreadyExistsError,
        match="already exists",
    ):
        await use_case.execute(
            CreateApplicationCommand(
                candidate_id=candidate_id,
                job_id=job_id,
                resume_id=uuid4(),
            ),
        )

    assert repository.created == []


@pytest.mark.asyncio
async def test_create_application_allows_same_candidate_for_different_job() -> None:
    candidate_id = uuid4()
    existing_job_id = uuid4()
    new_job_id = uuid4()

    existing = Application(
        id=uuid4(),
        candidate_id=candidate_id,
        job_id=existing_job_id,
        resume_id=uuid4(),
    )

    repository = FakeApplicationRepository(existing=existing)
    use_case = CreateApplication(repository)

    result = await use_case.execute(
        CreateApplicationCommand(
            candidate_id=candidate_id,
            job_id=new_job_id,
            resume_id=uuid4(),
        ),
    )

    assert result.candidate_id == candidate_id
    assert result.job_id == new_job_id
    assert len(repository.created) == 1


@pytest.mark.asyncio
async def test_create_application_allows_different_candidate_for_same_job() -> None:
    existing_job_id = uuid4()
    existing_candidate_id = uuid4()
    new_candidate_id = uuid4()

    existing = Application(
        id=uuid4(),
        candidate_id=existing_candidate_id,
        job_id=existing_job_id,
        resume_id=uuid4(),
    )

    repository = FakeApplicationRepository(existing=existing)
    use_case = CreateApplication(repository)

    result = await use_case.execute(
        CreateApplicationCommand(
            candidate_id=new_candidate_id,
            job_id=existing_job_id,
            resume_id=uuid4(),
        ),
    )

    assert result.candidate_id == new_candidate_id
    assert result.job_id == existing_job_id
    assert len(repository.created) == 1


@pytest.mark.asyncio
async def test_create_application_generates_unique_id() -> None:
    repository = FakeApplicationRepository()
    use_case = CreateApplication(repository)

    first = await use_case.execute(
        CreateApplicationCommand(
            candidate_id=uuid4(),
            job_id=uuid4(),
            resume_id=uuid4(),
        ),
    )

    second = await use_case.execute(
        CreateApplicationCommand(
            candidate_id=uuid4(),
            job_id=uuid4(),
            resume_id=uuid4(),
        ),
    )

    assert first.id != second.id
