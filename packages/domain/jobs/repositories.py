from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.jobs.entities import Job


class JobRepository(Protocol):
    """Persistence contract for job entities."""

    async def create(
        self,
        job: Job,
    ) -> Job:
        """Create and persist a job."""
        ...

    async def get_by_id(
        self,
        job_id: UUID,
    ) -> Job | None:
        """Return a job by ID."""
        ...

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        """Return a job by source URL."""
        ...

    async def list_all(self) -> Sequence[Job]:
        """Return all jobs."""
        ...

    async def update(
        self,
        job: Job,
    ) -> Job:
        """Update and persist a job."""
        ...

    async def delete(
        self,
        job_id: UUID,
    ) -> None:
        """Delete a job."""
        ...
