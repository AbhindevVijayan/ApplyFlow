from typing import Protocol
from uuid import UUID

from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)


class ApplicationSubmissionContextRepository(Protocol):
    """Contract for loading application submission context."""

    async def get_by_application_id(
        self,
        application_id: UUID,
    ) -> ApplicationSubmissionContext | None:
        """Return submission context for an application."""
        ...
