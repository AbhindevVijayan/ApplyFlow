from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.repositories.candidate import CandidateRepository
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


@pytest.mark.asyncio
async def test_create_and_get_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateRepository(session)

    candidate = Candidate(
        full_name="Repository Test Candidate",
        email="repository-test@example.com",
        phone="1234567890",
        location="Kerala",
    )

    created = await repository.create(candidate)
    await session.commit()

    assert created.id is not None
    assert created.full_name == "Repository Test Candidate"

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.email == "repository-test@example.com"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_candidate_by_email(
    session: AsyncSession,
) -> None:
    repository = CandidateRepository(session)

    candidate = Candidate(
        full_name="Email Lookup Candidate",
        email="email-lookup@example.com",
    )

    await repository.create(candidate)
    await session.commit()

    fetched = await repository.get_by_email(
        "email-lookup@example.com",
    )

    assert fetched is not None
    assert fetched.id == candidate.id
    assert fetched.full_name == "Email Lookup Candidate"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_nonexistent_candidate_returns_none(
    session: AsyncSession,
) -> None:
    repository = CandidateRepository(session)

    candidate = await repository.get_by_email(
        "does-not-exist@example.com",
    )

    assert candidate is None


@pytest.mark.asyncio
async def test_duplicate_email_raises_integrity_error(
    session: AsyncSession,
) -> None:
    repository = CandidateRepository(session)

    first = Candidate(
        full_name="First Candidate",
        email="duplicate-test@example.com",
    )

    second = Candidate(
        full_name="Second Candidate",
        email="duplicate-test@example.com",
    )

    await repository.create(first)
    await session.commit()

    with pytest.raises(IntegrityError):
        await repository.create(second)

    await session.rollback()

    existing = await repository.get_by_email(
        "duplicate-test@example.com",
    )

    assert existing is not None
    assert existing.id == first.id

    await repository.delete(existing)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateRepository(session)

    candidate = Candidate(
        full_name="Delete Test Candidate",
        email="delete-test@example.com",
    )

    await repository.create(candidate)
    await session.commit()

    candidate_id = candidate.id

    fetched = await repository.get_by_id(candidate_id)

    assert fetched is not None

    await repository.delete(fetched)
    await session.commit()

    deleted = await repository.get_by_id(candidate_id)

    assert deleted is None
