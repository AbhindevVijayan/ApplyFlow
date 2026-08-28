from datetime import date
from uuid import UUID

import pytest

from packages.application.candidates.list_education import ListEducation
from packages.domain.candidates.education import CandidateEducation


class FakeCandidateEducationRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.education: list[CandidateEducation] = []

    async def create(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        self.education.append(education)
        return education

    async def get_by_id(
        self,
        education_id: UUID,
    ) -> CandidateEducation | None:
        return next(
            (item for item in self.education if item.id == education_id),
            None,
        )

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateEducation]:
        return [item for item in self.education if item.candidate_id == candidate_id]

    async def update(
        self,
        education: CandidateEducation,
    ) -> CandidateEducation:
        for index, existing in enumerate(self.education):
            if existing.id == education.id:
                self.education[index] = education
                return education

        raise ValueError("Education not found")

    async def delete(
        self,
        education_id: UUID,
    ) -> None:
        self.education = [item for item in self.education if item.id != education_id]


@pytest.mark.asyncio
async def test_list_education_returns_candidate_education() -> None:
    candidate_id = UUID("11111111-1111-1111-1111-111111111111")

    education = CandidateEducation(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        candidate_id=candidate_id,
        institution="University of Kerala",
        degree="MCA",
        field_of_study="Computer Science",
        start_date=date(2023, 6, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
    )

    repository = FakeCandidateEducationRepository()
    repository.education.append(education)

    use_case = ListEducation(repository)

    result = await use_case.by_candidate(candidate_id)

    assert result == [education]


@pytest.mark.asyncio
async def test_list_education_returns_empty_list_when_none_exist() -> None:
    candidate_id = UUID("11111111-1111-1111-1111-111111111111")

    repository = FakeCandidateEducationRepository()
    use_case = ListEducation(repository)

    result = await use_case.by_candidate(candidate_id)

    assert result == []
