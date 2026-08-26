from packages.domain.applications.gateway import ApplicationSubmissionGateway
from packages.domain.applications.submission import (
    SubmissionResult,
    SubmissionStatus,
)
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)


class MockApplicationSubmissionGateway(ApplicationSubmissionGateway):
    """Development gateway that simulates an external submission."""

    async def submit(
        self,
        context: ApplicationSubmissionContext,
    ) -> SubmissionResult:
        """Simulate successful application submission."""

        return SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url=(f"https://example.com/applications/{context.application_id}"),
        )
