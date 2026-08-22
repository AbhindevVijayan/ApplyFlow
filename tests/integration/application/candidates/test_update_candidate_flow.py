from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.candidates.create_candidate import (
    CreateCandidate,
    CreateCandidateCommand,
)
from packages.application.candidates.delete_candidate import DeleteCandidate
from packages.application.candidates.update_candidate import (
    UpdateCandidate,
    UpdateCandidateCommand,
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
async def test_update_candidate_through_application(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    create_candidate = CreateCandidate(repository)
    update_candidate = UpdateCandidate(repository)
    delete_candidate = DeleteCandidate(repository)

    created = await create_candidate.execute(
        CreateCandidateCommand(
            full_name="Original Candidate",
            email=f"update-integration-{uuid4()}@example.com",
            phone="1234567890",
            location="Kerala",
        ),
    )

    await session.commit()

    updated = await update_candidate.execute(
        UpdateCandidateCommand(
            candidate_id=created.id,
            full_name="Updated Candidate",
            email="updated-integration@example.com",
            phone="9876543210",
            location="Bangalore",
        ),
    )

    await session.commit()

    assert updated.id == created.id
    assert updated.full_name == "Updated Candidate"
    assert updated.email == "updated-integration@example.com"
    assert updated.phone == "9876543210"
    assert updated.location == "Bangalore"

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.full_name == "Updated Candidate"
    assert fetched.email == "updated-integration@example.com"
    assert fetched.phone == "9876543210"
    assert fetched.location == "Bangalore"

    await delete_candidate.execute(created.id)
    await session.commit()
