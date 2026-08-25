from uuid import UUID

import pytest

from packages.application.candidates.get_education import (
    EducationNotFoundError,
    GetEducation,
)
from packages.domain.candidates.education import CandidateEducation


class FakeEducationRepository:
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
