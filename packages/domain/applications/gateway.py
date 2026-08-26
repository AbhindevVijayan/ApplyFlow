from typing import Protocol

from packages.domain.applications.submission import SubmissionResult
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)


class ApplicationSubmissionGateway(Protocol):
    """Contract for submitting applications to external systems."""

    async def submit(
        self,
        context: ApplicationSubmissionContext,
    ) -> SubmissionResult:
        """Submit an application to an external provider."""
        ...
