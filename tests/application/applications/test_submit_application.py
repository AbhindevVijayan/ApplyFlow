from datetime import UTC, datetime
from uuid import uuid4

import pytest

from packages.application.applications.submit_application import (
    ApplicationNotFoundError,
    ApplicationSubmissionContextNotFoundError,
    InvalidApplicationSubmissionError,
    SubmitApplication,
)
from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)
from packages.domain.applications.submission import (
    SubmissionResult,
    SubmissionStatus,
)
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)


class FakeApplicationRepository:
    def __init__(self, application: Application | None = None) -> None:
        self.application = application
        self.updated_application: Application | None = None

    async def create(self, application: Application) -> Application:
        return application

    async def get_by_id(self, application_id):
        if self.application is None:
            return None

        if self.application.id != application_id:
            return None

        return self.application

    async def get_by_candidate_id(self, candidate_id):
        return []

    async def get_by_job_id(self, job_id):
        return []

    async def get_by_candidate_and_job(self, candidate_id, job_id):
        return None

    async def update(self, application: Application) -> Application:
        self.updated_application = application
        self.application = application
        return application

    async def delete(self, application_id) -> None:
        return None


class FakeSubmissionContextRepository:
    def __init__(
        self,
        context: ApplicationSubmissionContext | None = None,
    ) -> None:
        self.context = context
        self.requested_application_id = None

    async def get_by_application_id(
        self,
        application_id,
    ) -> ApplicationSubmissionContext | None:
        self.requested_application_id = application_id
        return self.context


class FakeSubmissionGateway:
    def __init__(self, result: SubmissionResult) -> None:
        self.result = result
        self.submitted_context = None

    async def submit(
        self,
        context: ApplicationSubmissionContext,
    ) -> SubmissionResult:
        self.submitted_context = context
        return self.result


def make_application(
    status: ApplicationStatus = ApplicationStatus.READY,
) -> Application:
    return Application(
        id=uuid4(),
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_id=uuid4(),
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def make_submission_context(
    application: Application,
) -> ApplicationSubmissionContext:
    return ApplicationSubmissionContext(
        application_id=application.id,
        candidate_id=application.candidate_id,
        candidate_name="Test Candidate",
        candidate_email="test@example.com",
        candidate_phone="9876543210",
        job_id=application.job_id,
        job_title="Software Engineer",
        company="Test Company",
        source="test",
        source_url="https://example.com/jobs/test",
        resume_id=application.resume_id,
        resume_filename="resume.pdf",
        resume_storage_key="test-resumes/resume.pdf",
    )


@pytest.mark.asyncio
async def test_submit_application_raises_when_application_does_not_exist() -> None:
    repository = FakeApplicationRepository()

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
        ),
    )

    context_repository = FakeSubmissionContextRepository()

    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    application_id = uuid4()

    with pytest.raises(ApplicationNotFoundError):
        await use_case.execute(application_id)

    assert gateway.submitted_context is None


@pytest.mark.asyncio
async def test_submit_application_rejects_application_not_ready() -> None:
    application = make_application(ApplicationStatus.DRAFT)

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    with pytest.raises(InvalidApplicationSubmissionError):
        await use_case.execute(application.id)

    assert gateway.submitted_context is None
    assert repository.updated_application is None


@pytest.mark.asyncio
async def test_submit_application_marks_application_as_submitted() -> None:
    application = make_application(ApplicationStatus.READY)

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/123",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.id == application.id
    assert result.status == ApplicationStatus.SUBMITTED
    assert result.external_application_url == "https://example.com/application/123"
    assert result.failure_reason is None

    assert gateway.submitted_context is not None
    assert gateway.submitted_context.application_id == application.id
    assert repository.updated_application is not None
    assert repository.updated_application.status == ApplicationStatus.SUBMITTED


@pytest.mark.asyncio
async def test_submit_application_persists_failure_reason() -> None:
    application = make_application(ApplicationStatus.READY)

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.FAILED,
            failure_reason="External provider rejected the application.",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.id == application.id
    assert result.status == ApplicationStatus.READY
    assert result.failure_reason == ("External provider rejected the application.")

    assert gateway.submitted_context is not None
    assert gateway.submitted_context.application_id == application.id
    assert repository.updated_application is not None
    assert repository.updated_application.failure_reason == (
        "External provider rejected the application."
    )


@pytest.mark.asyncio
async def test_submit_application_preserves_existing_application_fields() -> None:
    application = Application(
        id=uuid4(),
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_id=uuid4(),
        status=ApplicationStatus.READY,
        notes="Tailored resume for backend role.",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/456",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.candidate_id == application.candidate_id
    assert result.job_id == application.job_id
    assert result.resume_id == application.resume_id
    assert result.notes == "Tailored resume for backend role."


@pytest.mark.asyncio
async def test_submit_application_rejects_already_submitted_application() -> None:
    application = make_application(ApplicationStatus.SUBMITTED)

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/789",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    with pytest.raises(InvalidApplicationSubmissionError):
        await use_case.execute(application.id)

    assert gateway.submitted_context is None
    assert repository.updated_application is None


@pytest.mark.asyncio
async def test_submit_application_can_retry_after_failure() -> None:
    application = Application(
        id=uuid4(),
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_id=uuid4(),
        status=ApplicationStatus.READY,
        failure_reason="Previous submission failed.",
    )

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/999",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.status == ApplicationStatus.SUBMITTED
    assert result.failure_reason is None
    assert result.external_application_url == ("https://example.com/application/999")


@pytest.mark.asyncio
async def test_submit_application_sets_applied_at_after_success() -> None:
    application = make_application(ApplicationStatus.READY)

    assert application.applied_at is None

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/1000",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.status == ApplicationStatus.SUBMITTED
    assert result.applied_at is not None


@pytest.mark.asyncio
async def test_submit_application_preserves_existing_applied_at() -> None:
    existing_applied_at = datetime.now(UTC)

    application = Application(
        id=uuid4(),
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_id=uuid4(),
        status=ApplicationStatus.READY,
        applied_at=existing_applied_at,
    )

    repository = FakeApplicationRepository(application)

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url="https://example.com/application/1001",
        ),
    )

    context_repository = FakeSubmissionContextRepository(
        make_submission_context(application),
    )
    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    result = await use_case.execute(application.id)

    assert result.applied_at == existing_applied_at


@pytest.mark.asyncio
async def test_submit_application_raises_when_submission_context_does_not_exist() -> None:
    application = make_application(ApplicationStatus.READY)

    repository = FakeApplicationRepository(application)
    context_repository = FakeSubmissionContextRepository()

    gateway = FakeSubmissionGateway(
        SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
        ),
    )

    use_case = SubmitApplication(
        repository=repository,
        submission_context_repository=context_repository,
        gateway=gateway,
    )

    with pytest.raises(ApplicationSubmissionContextNotFoundError):
        await use_case.execute(application.id)

    assert context_repository.requested_application_id == application.id
    assert gateway.submitted_context is None
    assert repository.updated_application is None
