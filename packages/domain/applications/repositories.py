from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.applications.entities import Application


class ApplicationRepository(Protocol):
    """Persistence contract for application entities."""

    async def create(
        self,
        application: Application,
    ) -> Application:
        """Persist a new application."""
        ...

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> Application | None:
        """Return an application by ID."""
        ...

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Sequence[Application]:
        """Return applications belonging to a candidate."""
        ...

    async def get_by_job_id(
        self,
        job_id: UUID,
    ) -> Sequence[Application]:
        """Return applications for a job."""
        ...

    async def get_by_candidate_and_job(
        self,
        candidate_id: UUID,
        job_id: UUID,
    ) -> Application | None:
        """Return an application for a candidate/job pair."""
        ...

    async def update(
        self,
        application: Application,
    ) -> Application:
        """Update an existing application."""
        ...

    async def delete(
        self,
        application_id: UUID,
    ) -> None:
        """Delete an application by ID."""
        ...
