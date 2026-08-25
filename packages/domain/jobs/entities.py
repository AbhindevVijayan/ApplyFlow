from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Job:
    """Domain representation of a job posting."""

    id: UUID
    company: str
    title: str
    source: str
    source_url: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    required_skills: tuple[str, ...] = ()
    discovered_at: datetime | None = None
    created_at: datetime | None = None
