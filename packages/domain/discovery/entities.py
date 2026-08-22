from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DiscoveredJob:
    """A job posting discovered from an external source."""

    company: str
    title: str
    source: str
    source_url: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    discovered_at: datetime | None = None
