from uuid import uuid4

import pytest

from packages.domain.applications.submission import SubmissionStatus
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)
from packages.infrastructure.applications.submission.mock import (
    MockApplicationSubmissionGateway,
)


@pytest.mark.asyncio
async def test_mock_submission_gateway_returns_successful_result() -> None:
    gateway = MockApplicationSubmissionGateway()

    application_id = uuid4()

    context = ApplicationSubmissionContext(
        application_id=application_id,
        candidate_id=uuid4(),
        candidate_name="Test Candidate",
        candidate_email="test@example.com",
        candidate_phone="9876543210",
        job_id=uuid4(),
        job_title="Software Engineer",
        company="Test Company",
        source="greenhouse",
        source_url="https://example.com/jobs/123",
        resume_id=uuid4(),
        resume_filename="resume.pdf",
        resume_storage_key="resumes/test/resume.pdf",
    )

    result = await gateway.submit(context)

    assert result.status == SubmissionStatus.SUBMITTED
    assert result.external_application_url == f"https://example.com/applications/{application_id}"
