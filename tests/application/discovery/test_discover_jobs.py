from datetime import UTC, datetime
from uuid import uuid4

import pytest

from packages.application.discovery.discover_jobs import DiscoverJobs
from packages.domain.discovery.entities import DiscoveredJob
from packages.domain.jobs.entities import Job
from packages.infrastructure.requirements.keyword_extractor import (
    KeywordJobRequirementsExtractor,
)


class FakeJobSource:
    """Fake external source for application tests."""

    def __init__(
        self,
        jobs: list[DiscoveredJob],
    ) -> None:
        self._jobs = jobs

    @property
    def name(self) -> str:
        return "fake"

    async def discover(self) -> list[DiscoveredJob]:
        return self._jobs


class FakeJobRepository:
    """In-memory repository for application tests."""

    def __init__(self) -> None:
        self.jobs: list[Job] = []

    async def create(self, job: Job) -> Job:
        self.jobs.append(job)
        return job

    async def get_by_id(self, job_id):
        return next(
            (job for job in self.jobs if job.id == job_id),
            None,
        )

    async def get_by_source_url(self, source_url: str):
        return next(
            (job for job in self.jobs if job.source_url == source_url),
            None,
        )

    async def list_all(self):
        return list(self.jobs)

    async def update(self, job: Job) -> Job:
        for index, existing in enumerate(self.jobs):
            if existing.id == job.id:
                self.jobs[index] = job
                return job

        raise ValueError("Job not found.")

    async def delete(self, job_id) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]


@pytest.mark.asyncio
async def test_discover_jobs_persists_discovered_jobs() -> None:
    discovered_at = datetime.now(UTC)

    source = FakeJobSource(
        [
            DiscoveredJob(
                company="Acme",
                title="Python Developer",
                source="fake",
                source_url=f"https://example.com/{uuid4()}",
                description="Python backend development.",
                location="Remote",
                employment_type="Full-time",
                discovered_at=discovered_at,
            ),
        ],
    )

    repository = FakeJobRepository()

    use_case = DiscoverJobs(
        source=source,
        repository=repository,
        requirements_extractor=KeywordJobRequirementsExtractor(),
    )

    result = await use_case.execute()

    assert result.discovered_count == 1
    assert result.persisted_count == 1
    assert result.duplicate_count == 0
    assert len(result.jobs) == 1

    job = result.jobs[0]

    assert job.company == "Acme"
    assert job.title == "Python Developer"
    assert job.source == "fake"
    assert job.description == "Python backend development."
    assert job.location == "Remote"
    assert job.employment_type == "Full-time"
    assert job.discovered_at == discovered_at

    assert len(repository.jobs) == 1


@pytest.mark.asyncio
async def test_discover_jobs_skips_existing_source_urls() -> None:
    source_url = f"https://example.com/{uuid4()}"

    source = FakeJobSource(
        [
            DiscoveredJob(
                company="Acme",
                title="Python Developer",
                source="fake",
                source_url=source_url,
            ),
            DiscoveredJob(
                company="Acme",
                title="Python Developer",
                source="fake",
                source_url=source_url,
            ),
        ],
    )

    repository = FakeJobRepository()

    use_case = DiscoverJobs(
        source=source,
        repository=repository,
        requirements_extractor=KeywordJobRequirementsExtractor(),
    )

    result = await use_case.execute()

    assert result.discovered_count == 2
    assert result.persisted_count == 1
    assert result.duplicate_count == 1
    assert len(result.jobs) == 1

    assert len(repository.jobs) == 1


@pytest.mark.asyncio
async def test_discover_jobs_returns_empty_result_when_source_is_empty() -> None:
    source = FakeJobSource([])

    repository = FakeJobRepository()

    use_case = DiscoverJobs(
        source=source,
        repository=repository,
        requirements_extractor=KeywordJobRequirementsExtractor(),
    )

    result = await use_case.execute()

    assert result.discovered_count == 0
    assert result.persisted_count == 0
    assert result.duplicate_count == 0
    assert result.jobs == ()

    assert repository.jobs == []
