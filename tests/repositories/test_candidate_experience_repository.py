from collections.abc import AsyncGenerator
from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.models.candidate_experience import CandidateExperience
from packages.database.repositories.candidate_experience import (
    CandidateExperienceRepository,
)
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def candidate(session: AsyncSession) -> Candidate:
    candidate = Candidate(
        full_name="Experience Test Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    return candidate


@pytest.mark.asyncio
async def test_create_and_get_experience(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateExperienceRepository(session)

    experience = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Anjali Bakery",
        job_title="Software Developer",
        employment_type="Full-time",
        location="Kerala, India",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
        description="Developed and maintained internal software systems.",
        is_current=False,
    )

    created = await repository.create(experience)
    await session.commit()

    assert created.id is not None
    assert created.candidate_id == candidate.id
    assert created.company_name == "Anjali Bakery"
    assert created.job_title == "Software Developer"
    assert created.employment_type == "Full-time"
    assert created.location == "Kerala, India"
    assert created.start_date == date(2024, 1, 1)
    assert created.end_date == date(2025, 1, 1)
    assert created.is_current is False

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.company_name == "Anjali Bakery"
    assert fetched.job_title == "Software Developer"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(
    session: AsyncSession,
) -> None:
    repository = CandidateExperienceRepository(session)

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_candidate_id(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateExperienceRepository(session)

    older = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Company A",
        job_title="Junior Developer",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 1, 1),
    )

    newer = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Company B",
        job_title="Software Developer",
        start_date=date(2024, 1, 1),
        end_date=None,
        is_current=True,
    )

    await repository.create(older)
    await repository.create(newer)
    await session.commit()

    experiences = await repository.get_by_candidate_id(candidate.id)

    assert len(experiences) == 2
    assert {item.id for item in experiences} == {
        older.id,
        newer.id,
    }

    # Newest experience should appear first.
    assert experiences[0].id == newer.id
    assert experiences[1].id == older.id

    await repository.delete(older)
    await repository.delete(newer)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_candidate_id_returns_empty_list_for_unknown_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateExperienceRepository(session)

    experiences = await repository.get_by_candidate_id(uuid4())

    assert experiences == []


@pytest.mark.asyncio
async def test_update_experience(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateExperienceRepository(session)

    experience = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Original Company",
        job_title="Junior Developer",
        employment_type="Full-time",
    )

    await repository.create(experience)
    await session.commit()

    experience.company_name = "Updated Company"
    experience.job_title = "Senior Developer"
    experience.employment_type = "Contract"
    experience.location = "Bengaluru, India"
    experience.description = "Updated professional experience."
    experience.is_current = True

    updated = await repository.update(experience)
    await session.commit()

    assert updated.company_name == "Updated Company"
    assert updated.job_title == "Senior Developer"
    assert updated.employment_type == "Contract"
    assert updated.location == "Bengaluru, India"
    assert updated.description == "Updated professional experience."
    assert updated.is_current is True

    fetched = await repository.get_by_id(experience.id)

    assert fetched is not None
    assert fetched.company_name == "Updated Company"
    assert fetched.job_title == "Senior Developer"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_update_missing_experience_raises(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateExperienceRepository(session)

    experience = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Missing Company",
        job_title="Developer",
    )

    with pytest.raises(
        ValueError,
        match="Candidate experience not found",
    ):
        await repository.update(experience)


@pytest.mark.asyncio
async def test_delete_experience(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateExperienceRepository(session)

    experience = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Delete Company",
        job_title="Developer",
    )

    await repository.create(experience)
    await session.commit()

    experience_id = experience.id

    fetched = await repository.get_by_id(experience_id)

    assert fetched is not None

    await repository.delete(fetched)
    await session.commit()

    deleted = await repository.get_by_id(experience_id)

    assert deleted is None


@pytest.mark.asyncio
async def test_delete_candidate_cascades_to_experience(
    session: AsyncSession,
) -> None:
    candidate = Candidate(
        full_name="Cascade Experience Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    repository = CandidateExperienceRepository(session)

    experience = CandidateExperience(
        candidate_id=candidate.id,
        company_name="Cascade Company",
        job_title="Developer",
    )

    await repository.create(experience)
    await session.commit()

    experience_id = experience.id

    await session.delete(candidate)
    await session.commit()

    assert await repository.get_by_id(experience_id) is None
