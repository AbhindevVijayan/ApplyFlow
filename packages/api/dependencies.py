from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.applications.submit_application import SubmitApplication
from packages.application.discovery.run_discovery import RunDiscovery
from packages.config.settings import get_settings
from packages.database.repositories.application_adapter import (
    ApplicationRepositoryAdapter,
)
from packages.database.repositories.application_submission_context import (
    DatabaseApplicationSubmissionContextRepository,
)
from packages.database.repositories.candidate_adapter import CandidateRepositoryAdapter
from packages.database.repositories.job_adapter import JobRepositoryAdapter
from packages.database.repositories.skill_adapter import SkillRepositoryAdapter
from packages.database.session import get_session
from packages.infrastructure.applications.submission.mock import (
    MockApplicationSubmissionGateway,
)
from packages.infrastructure.discovery.greenhouse.client import GreenhouseClient
from packages.infrastructure.discovery.greenhouse.source import GreenhouseJobSource

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


async def get_discovery_use_case(
    session: SessionDependency,
) -> AsyncIterator[RunDiscovery]:
    """Build the job discovery use case for the current request."""

    settings = get_settings()

    repository = JobRepositoryAdapter(session)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0),
    ) as http_client:
        sources = [
            GreenhouseJobSource(
                GreenhouseClient(
                    board_token,
                    client=http_client,
                ),
            )
            for board_token in settings.greenhouse_boards()
        ]

        yield RunDiscovery(
            sources=sources,
            repository=repository,
        )


def get_skill_repository(
    session: SessionDependency,
) -> SkillRepositoryAdapter:
    """Build the skill repository for the current request."""
    return SkillRepositoryAdapter(session)


def get_candidate_repository(
    session: SessionDependency,
) -> CandidateRepositoryAdapter:
    """Build the candidate repository for the current request."""
    return CandidateRepositoryAdapter(session)


def get_submit_application_use_case(
    session: SessionDependency,
) -> SubmitApplication:
    """Build the application submission use case for the current request."""

    repository = ApplicationRepositoryAdapter(session)
    submission_context_repository = DatabaseApplicationSubmissionContextRepository(session)
    gateway = MockApplicationSubmissionGateway()

    return SubmitApplication(
        repository=repository,
        submission_context_repository=submission_context_repository,
        gateway=gateway,
    )


SubmitApplicationDependency = Annotated[
    SubmitApplication,
    Depends(get_submit_application_use_case),
]
