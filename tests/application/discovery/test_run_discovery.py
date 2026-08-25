from datetime import datetime

import pytest

from packages.application.discovery.run_discovery import (
    DiscoveryResult,
    RunDiscovery,
)
from packages.domain.discovery.entities import DiscoveredJob
from packages.domain.jobs.entities import Job


class FakeJobSource:
    def __init__(
        self,
        name: str,
        jobs: list[DiscoveredJob],
    ) -> None:
        self._name = name
        self._jobs = jobs

    @property
    def name(self) -> str:
        return self._name

    async def discover(self) -> list[DiscoveredJob]:
        return self._jobs


class FakeJobRepository:
    def __init__(self) -> None:
        self.jobs: list[Job] = []

    async def create(self, job: Job) -> Job:
        self.jobs.append(job)
        return job

    async def get_by_id(self, job_id: object) -> Job | None:
        return next(
            (job for job in self.jobs if job.id == job_id),
            None,
        )

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        return next(
            (job for job in self.jobs if job.source_url == source_url),
            None,
        )

    async def list_all(self) -> list[Job]:
        return self.jobs

    async def update(self, job: Job) -> Job:
        for index, existing in enumerate(self.jobs):
            if existing.id == job.id:
                self.jobs[index] = job
                return job

        raise ValueError("Job does not exist.")

    async def delete(self, job_id: object) -> None:
        self.jobs = [job for job in self.jobs if job.id != job_id]


def make_discovered_job(
    *,
    company: str,
    title: str,
    source_url: str,
) -> DiscoveredJob:
    return DiscoveredJob(
        company=company,
        title=title,
        source="greenhouse",
        source_url=source_url,
        discovered_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_run_discovery_persists_jobs() -> None:
    repository = FakeJobRepository()

    source = FakeJobSource(
        "greenhouse",
        [
            make_discovered_job(
                company="Acme",
                title="Python Developer",
                source_url="https://example.com/jobs/1",
            ),
        ],
    )

    use_case = RunDiscovery(
        sources=[source],
        repository=repository,
    )

    results = await use_case.execute()

    assert len(results) == 1
    assert isinstance(results[0], DiscoveryResult)
    assert results[0].source == "greenhouse"
    assert len(results[0].jobs) == 1
    assert results[0].jobs[0].company == "Acme"

    assert len(repository.jobs) == 1
    assert repository.jobs[0].title == "Python Developer"


@pytest.mark.asyncio
async def test_run_discovery_runs_multiple_sources() -> None:
    repository = FakeJobRepository()

    greenhouse = FakeJobSource(
        "greenhouse",
        [
            make_discovered_job(
                company="Acme",
                title="Python Developer",
                source_url="https://example.com/jobs/1",
            ),
        ],
    )

    another_source = FakeJobSource(
        "another-source",
        [
            make_discovered_job(
                company="Globex",
                title="Backend Engineer",
                source_url="https://example.com/jobs/2",
            ),
        ],
    )

    use_case = RunDiscovery(
        sources=[greenhouse, another_source],
        repository=repository,
    )

    results = await use_case.execute()

    assert len(results) == 2

    assert results[0].source == "greenhouse"
    assert results[1].source == "another-source"

    assert len(results[0].jobs) == 1
    assert len(results[1].jobs) == 1

    assert len(repository.jobs) == 2


@pytest.mark.asyncio
async def test_run_discovery_skips_duplicate_jobs() -> None:
    repository = FakeJobRepository()

    job = make_discovered_job(
        company="Acme",
        title="Python Developer",
        source_url="https://example.com/jobs/1",
    )

    source = FakeJobSource(
        "greenhouse",
        [job, job],
    )

    use_case = RunDiscovery(
        sources=[source],
        repository=repository,
    )

    results = await use_case.execute()

    assert len(results) == 1
    assert len(results[0].jobs) == 1
    assert len(repository.jobs) == 1


class FailingJobSource:
    def __init__(
        self,
        name: str,
        error: Exception,
    ) -> None:
        self._name = name
        self._error = error

    @property
    def name(self) -> str:
        return self._name

    async def discover(self) -> list[DiscoveredJob]:
        raise self._error


@pytest.mark.asyncio
async def test_run_discovery_isolates_source_failures() -> None:
    repository = FakeJobRepository()

    failing_source = FailingJobSource(
        "failing-source",
        RuntimeError("upstream unavailable"),
    )

    working_source = FakeJobSource(
        "working-source",
        [
            make_discovered_job(
                company="Acme",
                title="Python Developer",
                source_url="https://example.com/jobs/1",
            ),
        ],
    )

    use_case = RunDiscovery(
        sources=[failing_source, working_source],
        repository=repository,
    )

    results = await use_case.execute()

    assert len(results) == 2

    failed = results[0]
    assert failed.source == "failing-source"
    assert failed.status == "failed"
    assert failed.jobs == ()
    assert failed.error == "upstream unavailable"

    completed = results[1]
    assert completed.source == "working-source"
    assert completed.status == "completed"
    assert len(completed.jobs) == 1
    assert completed.error is None

    assert len(repository.jobs) == 1
