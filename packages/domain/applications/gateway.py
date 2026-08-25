from typing import Protocol
from uuid import UUID

from packages.domain.applications.submission import SubmissionResult


class ApplicationSubmissionGateway(Protocol):
    """Contract for submitting applications to external systems."""

    async def submit(
        self,
        application_id: UUID,
    ) -> SubmissionResult:
        """Submit an application to an external provider."""
        ...
