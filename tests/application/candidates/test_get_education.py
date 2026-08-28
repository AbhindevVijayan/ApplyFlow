from uuid import UUID

import pytest

from packages.application.candidates.get_education import (
    EducationNotFoundError,
    GetEducation,
)
from packages.domain.candidates.education import CandidateEducation


class FakeEducationRepository:
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
async def test_get_education_returns_education() -> None:
    repository = FakeEducationRepository()

    education = CandidateEducation(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        candidate_id=UUID("22222222-2222-2222-2222-222222222222"),
        institution="University of Kerala",
        degree="MCA",
    )

    repository.education.append(education)

    result = await GetEducation(repository).execute(education.id)

    assert result == education


@pytest.mark.asyncio
async def test_get_education_rejects_missing_education() -> None:
    repository = FakeEducationRepository()
    education_id = UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(
        EducationNotFoundError,
        match=f"Candidate education '{education_id}' was not found.",
    ):
        await GetEducation(repository).execute(education_id)
