from dataclasses import dataclass
from datetime import datetime
from typing import Final, TypeGuard
from uuid import UUID

from packages.domain.jobs.entities import Job
from packages.domain.jobs.repositories import JobRepository


class Unset:
    """Sentinel representing an omitted update field."""


UNSET: Final = Unset()


def is_set(value: str | Unset) -> TypeGuard[str]:
    """Return True when a required string field was supplied."""
    return not isinstance(value, Unset)


def is_optional_string_set(
    value: str | None | Unset,
) -> TypeGuard[str | None]:
    """Return True when an optional string field was supplied."""
    return not isinstance(value, Unset)


def is_datetime_set(
    value: datetime | None | Unset,
) -> TypeGuard[datetime | None]:
    """Return True when a datetime field was supplied."""
    return not isinstance(value, Unset)


class JobNotFoundError(Exception):
    """Raised when the requested job does not exist."""


class JobSourceURLAlreadyExistsError(Exception):
    """Raised when the requested source URL belongs to another job."""


@dataclass(frozen=True, slots=True)
class UpdateJobCommand:
    """Fields that may be changed on a job."""

    job_id: UUID
    company: str | Unset = UNSET
    title: str | Unset = UNSET
    source: str | Unset = UNSET
    source_url: str | Unset = UNSET
    description: str | None | Unset = UNSET
    location: str | None | Unset = UNSET
    employment_type: str | None | Unset = UNSET
    discovered_at: datetime | None | Unset = UNSET


class UpdateJob:
    """Use case for updating a job."""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateJobCommand,
    ) -> Job:
        """Update and persist a job."""

        job = await self._repository.get_by_id(command.job_id)

        if job is None:
            raise JobNotFoundError(
                f"Job '{command.job_id}' was not found.",
            )

        if is_set(command.source_url) and command.source_url != job.source_url:
            existing = await self._repository.get_by_source_url(
                command.source_url,
            )

            if existing is not None and existing.id != job.id:
                raise JobSourceURLAlreadyExistsError(
                    f"Job with source URL '{command.source_url}' already exists.",
                )

        company = command.company if is_set(command.company) else job.company

        title = command.title if is_set(command.title) else job.title

        source = command.source if is_set(command.source) else job.source

        source_url = command.source_url if is_set(command.source_url) else job.source_url

        description = (
            command.description if is_optional_string_set(command.description) else job.description
        )

        location = command.location if is_optional_string_set(command.location) else job.location

        employment_type = (
            command.employment_type
            if is_optional_string_set(command.employment_type)
            else job.employment_type
        )

        discovered_at = (
            command.discovered_at if is_datetime_set(command.discovered_at) else job.discovered_at
        )

        updated = Job(
            id=job.id,
            company=company,
            title=title,
            source=source,
            source_url=source_url,
            description=description,
            location=location,
            employment_type=employment_type,
            discovered_at=discovered_at,
            created_at=job.created_at,
        )

        return await self._repository.update(updated)
