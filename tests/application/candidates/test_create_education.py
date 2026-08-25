from datetime import date
from uuid import UUID

import pytest

from packages.application.candidates.create_education import (
    CreateEducation,
    CreateEducationCommand,
    InvalidEducationError,
)
from packages.domain.candidates.education import CandidateEducation


class FakeEducationRepository:
    """In-memory repository for education application tests."""

    def __init__(self) -> None:
        self.education: list[CandidateEducation] = []

    async def create(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        self.education.append(education)
        return education


@pytest.mark.asyncio
async def test_create_education_creates_and_returns_education() -> None:
    repository = FakeEducationRepository()
    use_case = CreateEducation(repository)

    candidate_id = UUID("11111111-1111-1111-1111-111111111111")

    command = CreateEducationCommand(
        candidate_id=candidate_id,
        institution="Mahatma Gandhi University",
        degree="MCA",
        field_of_study="Computer Science",
        start_date=date(2024, 6, 1),
        end_date=date(2026, 4, 30),
        grade="8.2 CGPA",
    )

    education = await use_case.execute(command)

    assert education.id is not None
    assert isinstance(education.id, UUID)
    assert education.candidate_id == candidate_id
    assert education.institution == "Mahatma Gandhi University"
    assert education.degree == "MCA"
    assert education.field_of_study == "Computer Science"
    assert education.start_date == date(2024, 6, 1)
    assert education.end_date == date(2026, 4, 30)
    assert education.grade == "8.2 CGPA"
    assert education.is_current is False

    assert repository.education == [education]


@pytest.mark.asyncio
async def test_create_education_rejects_end_date_before_start_date() -> None:
    repository = FakeEducationRepository()
    use_case = CreateEducation(repository)

    command = CreateEducationCommand(
        candidate_id=UUID("11111111-1111-1111-1111-111111111111"),
        institution="University",
        degree="MCA",
        start_date=date(2026, 1, 1),
        end_date=date(2025, 12, 31),
    )

    with pytest.raises(
        InvalidEducationError,
        match="end_date cannot be earlier than start_date.",
    ):
        await use_case.execute(command)

    assert repository.education == []


@pytest.mark.asyncio
async def test_create_education_rejects_current_education_with_end_date() -> None:
    repository = FakeEducationRepository()
    use_case = CreateEducation(repository)

    command = CreateEducationCommand(
        candidate_id=UUID("11111111-1111-1111-1111-111111111111"),
        institution="University",
        degree="MCA",
        start_date=date(2024, 6, 1),
        end_date=date(2026, 4, 30),
        is_current=True,
    )

    with pytest.raises(
        InvalidEducationError,
        match="Current education cannot have an end_date.",
    ):
        await use_case.execute(command)

    assert repository.education == []
