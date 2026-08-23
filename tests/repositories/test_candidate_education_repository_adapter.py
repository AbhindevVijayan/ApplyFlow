from collections.abc import AsyncGenerator
from datetime import date
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.repositories.candidate_education_adapter import (
    CandidateEducationRepositoryAdapter,
)
from packages.database.session import SessionFactory
from packages.domain.candidates.education import CandidateEducation


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def adapter(
    session: AsyncSession,
) -> CandidateEducationRepositoryAdapter:
    return CandidateEducationRepositoryAdapter(session)


@pytest.fixture
async def candidate_id(
    session: AsyncSession,
) -> UUID:
    candidate = Candidate(
        id=uuid4(),
        full_name="Test Candidate",
        email=f"test-{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.flush()

    return candidate.id


@pytest.mark.asyncio
async def test_adapter_creates_and_returns_domain_education(
    adapter: CandidateEducationRepositoryAdapter,
    candidate_id: object,
) -> None:
    education = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="University of Kerala",
        degree="MCA",
        field_of_study="Computer Science",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
        is_current=False,
    )

    created = await adapter.create(education)

    assert isinstance(created, CandidateEducation)
    assert created.id == education.id
    assert created.candidate_id == candidate_id
    assert created.institution == "University of Kerala"
    assert created.degree == "MCA"
    assert created.field_of_study == "Computer Science"
    assert created.start_date == date(2023, 6, 1)
    assert created.end_date == date(2025, 5, 31)
    assert created.grade == "8.2 CGPA"
    assert created.is_current is False

    await adapter.delete(created.id)
    await adapter._repository._session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_id_returns_domain_education(
    adapter: CandidateEducationRepositoryAdapter,
    candidate_id: object,
) -> None:
    education = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="University of Kerala",
        degree="MCA",
    )

    created = await adapter.create(education)
    await adapter._repository._session.commit()

    result = await adapter.get_by_id(created.id)

    assert result is not None
    assert isinstance(result, CandidateEducation)
    assert result.id == created.id
    assert result.institution == "University of Kerala"
    assert result.degree == "MCA"

    await adapter.delete(created.id)
    await adapter._repository._session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_id_returns_none_when_missing(
    adapter: CandidateEducationRepositoryAdapter,
) -> None:
    result = await adapter.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_adapter_get_by_candidate_id_returns_domain_education(
    adapter: CandidateEducationRepositoryAdapter,
    candidate_id: object,
) -> None:
    first = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="College A",
        degree="BSc",
        start_date=date(2019, 6, 1),
        end_date=date(2022, 5, 31),
    )

    second = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="University B",
        degree="MCA",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
    )

    await adapter.create(first)
    await adapter.create(second)
    await adapter._repository._session.commit()

    result = await adapter.get_by_candidate_id(candidate_id)

    assert len(result) == 2
    assert all(isinstance(item, CandidateEducation) for item in result)
    assert {item.id for item in result} == {first.id, second.id}

    await adapter.delete(first.id)
    await adapter.delete(second.id)
    await adapter._repository._session.commit()


@pytest.mark.asyncio
async def test_adapter_update_returns_domain_education(
    adapter: CandidateEducationRepositoryAdapter,
    candidate_id: object,
) -> None:
    education = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="Original University",
        degree="BSc",
    )

    await adapter.create(education)
    await adapter._repository._session.commit()

    updated_education = CandidateEducation(
        id=education.id,
        candidate_id=candidate_id,
        institution="Updated University",
        degree="MCA",
        grade="8.5 CGPA",
    )

    result = await adapter.update(updated_education)

    assert isinstance(result, CandidateEducation)
    assert result.id == education.id
    assert result.institution == "Updated University"
    assert result.degree == "MCA"
    assert result.grade == "8.5 CGPA"

    await adapter.delete(result.id)
    await adapter._repository._session.commit()


@pytest.mark.asyncio
async def test_adapter_delete_removes_education(
    adapter: CandidateEducationRepositoryAdapter,
    candidate_id: object,
) -> None:
    education = CandidateEducation(
        id=uuid4(),
        candidate_id=candidate_id,
        institution="Delete University",
        degree="BSc",
    )

    created = await adapter.create(education)
    await adapter._repository._session.commit()

    await adapter.delete(created.id)
    await adapter._repository._session.commit()

    result = await adapter.get_by_id(created.id)

    assert result is None


@pytest.mark.asyncio
async def test_adapter_delete_is_safe_when_education_does_not_exist(
    adapter: CandidateEducationRepositoryAdapter,
) -> None:
    await adapter.delete(uuid4())
