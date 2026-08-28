from typing import Protocol

from packages.domain.requirements.entities import JobRequirements


class JobRequirementsExtractor(Protocol):
    """Contract for extracting requirements from job postings."""

    def extract(
        self,
        description: str | None,
    ) -> JobRequirements:
        """Extract structured requirements from a job description."""
        ...
