from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.candidates.create_candidate import (
    CreateCandidate,
    CreateCandidateCommand,
)
from packages.application.candidates.delete_candidate import DeleteCandidate
from packages.application.candidates.get_candidate import (
    CandidateNotFoundError,
    GetCandidate,
)
from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.mark.asyncio
async def test_create_and_get_candidate_through_application(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    create_candidate = CreateCandidate(repository)
    get_candidate = GetCandidate(repository)
    delete_candidate = DeleteCandidate(repository)

    created = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Integration Candidate",
            email="integration-candidate@example.com",
            phone="9876543210",
            location="Kerala",
        ),
    )

    await session.commit()

    assert created.id is not None
    assert created.full_name == "Integration Candidate"
    assert created.email == "integration-candidate@example.com"

    fetched = await get_candidate.execute(created.id)

    assert fetched.id == created.id
    assert fetched.full_name == "Integration Candidate"
    assert fetched.email == "integration-candidate@example.com"
    assert fetched.phone == "9876543210"
    assert fetched.location == "Kerala"

    await delete_candidate.execute(created.id)
    await session.commit()

    with pytest.raises(CandidateNotFoundError):
        await get_candidate.execute(created.id)
