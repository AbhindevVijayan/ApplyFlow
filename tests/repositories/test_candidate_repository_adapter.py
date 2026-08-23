from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.domain.candidates.entities import Candidate


@pytest.mark.asyncio
async def test_adapter_creates_and_returns_domain_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    candidate = Candidate(
        id=uuid4(),
        full_name="Adapter Candidate",
        email="adapter-create@example.com",
        phone="1234567890",
        location="Kerala",
    )

    created = await repository.create(candidate)
    await session.commit()

    assert created.id is not None
    assert created.full_name == "Adapter Candidate"
    assert created.email == "adapter-create@example.com"
    assert created.phone == "1234567890"
    assert created.location == "Kerala"

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert isinstance(fetched, Candidate)
    assert fetched.id == created.id

    await repository.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_email_returns_domain_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    candidate = Candidate(
        id=uuid4(),
        full_name="Email Adapter Candidate",
        email="adapter-email@example.com",
    )

    created = await repository.create(candidate)
    await session.commit()

    fetched = await repository.get_by_email(
        "adapter-email@example.com",
    )

    assert fetched is not None
    assert isinstance(fetched, Candidate)
    assert fetched.id == created.id
    assert fetched.full_name == "Email Adapter Candidate"

    await repository.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_delete_uses_candidate_id(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    candidate = Candidate(
        id=uuid4(),
        full_name="Delete Adapter Candidate",
        email="adapter-delete@example.com",
    )

    created = await repository.create(candidate)
    await session.commit()

    assert created.id is not None

    await repository.delete(created.id)
    await session.commit()

    deleted = await repository.get_by_id(created.id)

    assert deleted is None


@pytest.mark.asyncio
async def test_adapter_list_all_returns_domain_candidates(
    session: AsyncSession,
) -> None:
    repository = CandidateRepositoryAdapter(session)

    first = await repository.create(
        Candidate(
            id=uuid4(),
            full_name="Adapter First",
            email="adapter-first@example.com",
        ),
    )

    second = await repository.create(
        Candidate(
            id=uuid4(),
            full_name="Adapter Second",
            email="adapter-second@example.com",
        ),
    )

    await session.commit()

    candidates = await repository.list_all()

    ids = {candidate.id for candidate in candidates}

    assert first.id in ids
    assert second.id in ids
    assert all(isinstance(candidate, Candidate) for candidate in candidates)

    await repository.delete(first.id)
    await repository.delete(second.id)
    await session.commit()
