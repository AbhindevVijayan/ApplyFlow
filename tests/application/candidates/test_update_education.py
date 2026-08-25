from datetime import date
from uuid import UUID

import pytest

from packages.application.candidates.update_education import (
    EducationNotFoundError,
    InvalidEducationError,
    UpdateEducation,
    UpdateEducationCommand,
)
from packages.domain.candidates.education import CandidateEducation


class FakeCandidateEducationRepository:
    def __init__(self) -> None:
        self.education: list[CandidateEducation] = []

    async def get_by_id(
        self,
        education_id: UUID,
    ) -> CandidateEducation | None:
        return next(
            (item for item in self.education if item.id == education_id),
            None,
        )

    async def update(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        for index, existing in enumerate(self.education):
            if existing.id == education.id:
                self.education[index] = education
                return education

        raise ValueError("Education not found")


@pytest.mark.asyncio
async def test_update_education_updates_existing_record() -> None:
    education_id = UUID("11111111-1111-1111-1111-111111111111")
    candidate_id = UUID("22222222-2222-2222-2222-222222222222")

    existing = CandidateEducation(
        id=education_id,
        candidate_id=candidate_id,
        institution="Old University",
        degree="BSc",
    )

    repository = FakeCandidateEducationRepository()
    repository.education.append(existing)

    command = UpdateEducationCommand(
        education_id=education_id,
        institution="University of Kerala",
        degree="MCA",
        field_of_study="Computer Science",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
    )

    result = await UpdateEducation(repository).execute(command)

    assert result.institution == "University of Kerala"
    assert result.degree == "MCA"
    assert result.field_of_study == "Computer Science"
    assert result.grade == "8.2 CGPA"
    assert result.candidate_id == candidate_id
    assert repository.education == [result]


@pytest.mark.asyncio
async def test_update_education_rejects_missing_education() -> None:
    education_id = UUID("11111111-1111-1111-1111-111111111111")

    repository = FakeCandidateEducationRepository()

    command = UpdateEducationCommand(
        education_id=education_id,
        institution="University of Kerala",
        degree="MCA",
    )

    with pytest.raises(
        EducationNotFoundError,
        match=f"Education '{education_id}' was not found.",
    ):
        await UpdateEducation(repository).execute(command)


@pytest.mark.asyncio
async def test_update_education_rejects_invalid_dates() -> None:
    repository = FakeCandidateEducationRepository()

    education = CandidateEducation(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        candidate_id=UUID("22222222-2222-2222-2222-222222222222"),
        institution="University",
        degree="MCA",
    )

    repository.education.append(education)

    command = UpdateEducationCommand(
        education_id=education.id,
        institution="University",
        degree="MCA",
        start_date=date(2025, 1, 1),
        end_date=date(2024, 1, 1),
    )

    with pytest.raises(
        InvalidEducationError,
        match="end_date cannot be earlier than start_date.",
    ):
        await UpdateEducation(repository).execute(command)


@pytest.mark.asyncio
async def test_update_education_rejects_current_with_end_date() -> None:
    repository = FakeCandidateEducationRepository()

    education = CandidateEducation(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        candidate_id=UUID("22222222-2222-2222-2222-222222222222"),
        institution="University",
        degree="MCA",
    )

    repository.education.append(education)

    command = UpdateEducationCommand(
        education_id=education.id,
        institution="University",
        degree="MCA",
        end_date=date(2025, 1, 1),
        is_current=True,
    )

    with pytest.raises(
        InvalidEducationError,
        match="Current education cannot have an end_date.",
    ):
        await UpdateEducation(repository).execute(command)
