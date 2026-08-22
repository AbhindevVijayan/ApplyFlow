from datetime import UTC, datetime

import pytest

from packages.domain.discovery.entities import DiscoveredJob


def test_discovered_job_contains_required_fields() -> None:
    job = DiscoveredJob(
        company="Acme",
        title="Python Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/123",
    )

    assert job.company == "Acme"
    assert job.title == "Python Developer"
    assert job.source == "greenhouse"
    assert job.source_url == "https://example.com/jobs/123"


def test_discovered_job_supports_optional_fields() -> None:
    discovered_at = datetime.now(UTC)

    job = DiscoveredJob(
        company="Acme",
        title="Python Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/123",
        description="Backend development.",
        location="Remote",
        employment_type="Full-time",
        discovered_at=discovered_at,
    )

    assert job.description == "Backend development."
    assert job.location == "Remote"
    assert job.employment_type == "Full-time"
    assert job.discovered_at == discovered_at


def test_discovered_job_is_immutable() -> None:
    job = DiscoveredJob(
        company="Acme",
        title="Python Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/123",
    )

    with pytest.raises(AttributeError):
        job.title = "Something Else"  # type: ignore[misc]
