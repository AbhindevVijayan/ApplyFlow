from collections.abc import AsyncGenerator
from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.models.candidate_education import CandidateEducation
from packages.database.repositories.candidate_education import (
    CandidateEducationRepository,
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
        full_name="Education Test Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    return candidate


@pytest.mark.asyncio
async def test_create_and_get_education(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateEducationRepository(session)

    education = CandidateEducation(
        candidate_id=candidate.id,
        institution="University of Kerala",
        degree="MCA",
        field_of_study="Computer Science",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
        is_current=False,
    )

    created = await repository.create(education)
    await session.commit()

    assert created.id is not None
    assert created.candidate_id == candidate.id
    assert created.institution == "University of Kerala"
    assert created.degree == "MCA"

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.field_of_study == "Computer Science"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_candidate_id(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateEducationRepository(session)

    first = CandidateEducation(
        candidate_id=candidate.id,
        institution="College A",
        degree="BSc",
        start_date=date(2019, 6, 1),
        end_date=date(2022, 5, 31),
    )

    second = CandidateEducation(
        candidate_id=candidate.id,
        institution="University B",
        degree="MCA",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
    )

    await repository.create(first)
    await repository.create(second)
    await session.commit()

    education = await repository.get_by_candidate_id(candidate.id)

    assert len(education) == 2
    assert {item.id for item in education} == {
        first.id,
        second.id,
    }

    await repository.delete(first)
    await repository.delete(second)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_candidate_id_returns_empty_list_for_unknown_candidate(
    session: AsyncSession,
) -> None:
    repository = CandidateEducationRepository(session)

    education = await repository.get_by_candidate_id(uuid4())

    assert education == []


@pytest.mark.asyncio
async def test_update_education(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateEducationRepository(session)

    education = CandidateEducation(
        candidate_id=candidate.id,
        institution="Original University",
        degree="BSc",
    )

    await repository.create(education)
    await session.commit()

    education.institution = "Updated University"
    education.degree = "MCA"
    education.grade = "8.5 CGPA"

    updated = await repository.update(education)
    await session.commit()

    assert updated.institution == "Updated University"
    assert updated.degree == "MCA"
    assert updated.grade == "8.5 CGPA"

    fetched = await repository.get_by_id(education.id)

    assert fetched is not None
    assert fetched.institution == "Updated University"

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_education(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = CandidateEducationRepository(session)

    education = CandidateEducation(
        candidate_id=candidate.id,
        institution="Delete University",
        degree="BSc",
    )

    await repository.create(education)
    await session.commit()

    education_id = education.id

    fetched = await repository.get_by_id(education_id)

    assert fetched is not None

    await repository.delete(fetched)
    await session.commit()

    deleted = await repository.get_by_id(education_id)

    assert deleted is None


@pytest.mark.asyncio
async def test_delete_candidate_cascades_to_education(
    session: AsyncSession,
) -> None:
    candidate = Candidate(
        full_name="Cascade Education Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    repository = CandidateEducationRepository(session)

    education = CandidateEducation(
        candidate_id=candidate.id,
        institution="Cascade University",
        degree="MCA",
    )

    await repository.create(education)
    await session.commit()

    education_id = education.id

    await session.delete(candidate)
    await session.commit()

    assert await repository.get_by_id(education_id) is None
