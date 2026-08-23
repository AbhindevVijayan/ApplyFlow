from collections.abc import AsyncGenerator
from datetime import date
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.repositories.candidate_experience_adapter import (
    CandidateExperienceRepositoryAdapter,
)
from packages.database.session import SessionFactory
from packages.domain.candidates.experience import CandidateExperience


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def candidate_id(
    session: AsyncSession,
) -> UUID:
    candidate = Candidate(
        full_name="Adapter Test Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    return candidate.id


@pytest.fixture
def adapter(
    session: AsyncSession,
) -> CandidateExperienceRepositoryAdapter:
    return CandidateExperienceRepositoryAdapter(session)


@pytest.mark.asyncio
async def test_adapter_creates_and_returns_domain_experience(
    session: AsyncSession,
    adapter: CandidateExperienceRepositoryAdapter,
    candidate_id: UUID,
) -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Anjali Bakery",
        job_title="Software Developer",
        employment_type="Full-time",
        location="Kerala, India",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
        description="Developed internal software systems.",
        is_current=False,
    )

    created = await adapter.create(experience)
    await session.commit()

    assert isinstance(created, CandidateExperience)
    assert created.id == experience.id
    assert created.candidate_id == candidate_id
    assert created.company_name == "Anjali Bakery"
    assert created.job_title == "Software Developer"
    assert created.employment_type == "Full-time"
    assert created.location == "Kerala, India"
    assert created.start_date == date(2024, 1, 1)
    assert created.end_date == date(2025, 1, 1)
    assert created.description == "Developed internal software systems."
    assert created.is_current is False

    await adapter.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_id_returns_domain_experience(
    session: AsyncSession,
    adapter: CandidateExperienceRepositoryAdapter,
    candidate_id: UUID,
) -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Company A",
        job_title="Developer",
        start_date=date(2023, 1, 1),
    )

    created = await adapter.create(experience)
    await session.commit()

    result = await adapter.get_by_id(created.id)

    assert result is not None
    assert isinstance(result, CandidateExperience)
    assert result.id == created.id
    assert result.company_name == "Company A"
    assert result.job_title == "Developer"

    await adapter.delete(created.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_get_by_id_returns_none_when_missing(
    adapter: CandidateExperienceRepositoryAdapter,
) -> None:
    result = await adapter.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_adapter_get_by_candidate_id_returns_domain_experiences(
    session: AsyncSession,
    adapter: CandidateExperienceRepositoryAdapter,
    candidate_id: UUID,
) -> None:
    older = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Company A",
        job_title="Junior Developer",
        start_date=date(2022, 1, 1),
    )

    newer = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Company B",
        job_title="Software Developer",
        start_date=date(2024, 1, 1),
        is_current=True,
    )

    await adapter.create(older)
    await adapter.create(newer)
    await session.commit()

    result = await adapter.get_by_candidate_id(candidate_id)

    assert len(result) == 2
    assert all(isinstance(item, CandidateExperience) for item in result)
    assert {item.id for item in result} == {older.id, newer.id}

    assert result[0].id == newer.id
    assert result[1].id == older.id

    await adapter.delete(older.id)
    await adapter.delete(newer.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_update_returns_domain_experience(
    session: AsyncSession,
    adapter: CandidateExperienceRepositoryAdapter,
    candidate_id: UUID,
) -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Original Company",
        job_title="Junior Developer",
    )

    await adapter.create(experience)
    await session.commit()

    updated_experience = CandidateExperience(
        id=experience.id,
        candidate_id=candidate_id,
        company_name="Updated Company",
        job_title="Senior Developer",
        employment_type="Full-time",
        location="Bengaluru, India",
        start_date=date(2024, 1, 1),
        description="Updated professional experience.",
        is_current=True,
    )

    result = await adapter.update(updated_experience)
    await session.commit()

    assert isinstance(result, CandidateExperience)
    assert result.id == experience.id
    assert result.company_name == "Updated Company"
    assert result.job_title == "Senior Developer"
    assert result.employment_type == "Full-time"
    assert result.location == "Bengaluru, India"
    assert result.start_date == date(2024, 1, 1)
    assert result.description == "Updated professional experience."
    assert result.is_current is True

    await adapter.delete(result.id)
    await session.commit()


@pytest.mark.asyncio
async def test_adapter_delete_removes_experience(
    session: AsyncSession,
    adapter: CandidateExperienceRepositoryAdapter,
    candidate_id: UUID,
) -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Delete Company",
        job_title="Developer",
    )

    created = await adapter.create(experience)
    await session.commit()

    await adapter.delete(created.id)
    await session.commit()

    result = await adapter.get_by_id(created.id)

    assert result is None


@pytest.mark.asyncio
async def test_adapter_delete_is_safe_when_experience_does_not_exist(
    adapter: CandidateExperienceRepositoryAdapter,
) -> None:
    await adapter.delete(uuid4())
