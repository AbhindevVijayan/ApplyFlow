from datetime import UTC, datetime
from uuid import uuid4

import pytest

from packages.application.applications.update_application import (
    ApplicationNotFoundError,
    UpdateApplication,
    UpdateApplicationCommand,
)
from packages.domain.applications.entities import (
    Application,
    ApplicationStatus,
)
from packages.domain.applications.lifecycle import (
    ALLOWED_TRANSITIONS,
    InvalidApplicationTransitionError,
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


def make_application(
    status: ApplicationStatus = ApplicationStatus.DRAFT,
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


@pytest.mark.asyncio
async def test_update_application_changes_status() -> None:
    application = make_application(ApplicationStatus.DRAFT)
    repository = FakeApplicationRepository(application)

    use_case = UpdateApplication(repository)

    result = await use_case.execute(
        UpdateApplicationCommand(
            application_id=application.id,
            status=ApplicationStatus.READY,
        ),
    )

    assert result.status == ApplicationStatus.READY
    assert repository.updated_application is not None
    assert repository.updated_application.status == ApplicationStatus.READY


@pytest.mark.asyncio
async def test_update_application_preserves_existing_fields() -> None:
    application = Application(
        id=uuid4(),
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_id=uuid4(),
        status=ApplicationStatus.READY,
        external_application_url="https://example.com/application",
        notes="Initial notes",
        failure_reason=None,
    )

    repository = FakeApplicationRepository(application)

    use_case = UpdateApplication(repository)

    result = await use_case.execute(
        UpdateApplicationCommand(
            application_id=application.id,
            notes="Updated notes",
        ),
    )

    assert result.status == ApplicationStatus.READY
    assert result.external_application_url == ("https://example.com/application")
    assert result.notes == "Updated notes"


@pytest.mark.asyncio
async def test_update_application_allows_valid_transition() -> None:
    valid_transitions = [
        (ApplicationStatus.DRAFT, ApplicationStatus.READY),
        (ApplicationStatus.READY, ApplicationStatus.SUBMITTED),
        (ApplicationStatus.SUBMITTED, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.SUBMITTED, ApplicationStatus.REJECTED),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER),
        (ApplicationStatus.OFFER, ApplicationStatus.WITHDRAWN),
    ]

    for current_status, new_status in valid_transitions:
        application = make_application(current_status)
        repository = FakeApplicationRepository(application)

        use_case = UpdateApplication(repository)

        result = await use_case.execute(
            UpdateApplicationCommand(
                application_id=application.id,
                status=new_status,
            ),
        )

        assert result.status == new_status


@pytest.mark.asyncio
async def test_update_application_rejects_invalid_transition() -> None:
    invalid_transitions = [
        (ApplicationStatus.DRAFT, ApplicationStatus.SUBMITTED),
        (ApplicationStatus.READY, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.REJECTED, ApplicationStatus.SUBMITTED),
        (ApplicationStatus.WITHDRAWN, ApplicationStatus.READY),
        (ApplicationStatus.OFFER, ApplicationStatus.SUBMITTED),
    ]

    for current_status, new_status in invalid_transitions:
        application = make_application(current_status)
        repository = FakeApplicationRepository(application)

        use_case = UpdateApplication(repository)

        with pytest.raises(InvalidApplicationTransitionError):
            await use_case.execute(
                UpdateApplicationCommand(
                    application_id=application.id,
                    status=new_status,
                ),
            )


@pytest.mark.asyncio
async def test_update_application_allows_non_status_update() -> None:
    application = make_application(ApplicationStatus.SUBMITTED)
    repository = FakeApplicationRepository(application)

    use_case = UpdateApplication(repository)

    result = await use_case.execute(
        UpdateApplicationCommand(
            application_id=application.id,
            notes="Candidate submitted application.",
        ),
    )

    assert result.status == ApplicationStatus.SUBMITTED
    assert result.notes == "Candidate submitted application."


@pytest.mark.asyncio
async def test_update_application_raises_when_application_missing() -> None:
    repository = FakeApplicationRepository()

    use_case = UpdateApplication(repository)

    application_id = uuid4()

    with pytest.raises(ApplicationNotFoundError):
        await use_case.execute(
            UpdateApplicationCommand(
                application_id=application_id,
                status=ApplicationStatus.READY,
            ),
        )


def test_allowed_transitions_are_explicit() -> None:
    assert ALLOWED_TRANSITIONS[ApplicationStatus.DRAFT] == frozenset(
        {
            ApplicationStatus.READY,
            ApplicationStatus.WITHDRAWN,
        },
    )

    assert ALLOWED_TRANSITIONS[ApplicationStatus.REJECTED] == frozenset()

    assert ALLOWED_TRANSITIONS[ApplicationStatus.WITHDRAWN] == frozenset()
