from uuid import UUID

import pytest

from packages.application.candidates.delete_education import (
    DeleteEducation,
    EducationNotFoundError,
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

    async def delete(self, education_id: UUID) -> None:
        self.education = [item for item in self.education if item.id != education_id]


@pytest.mark.asyncio
async def test_delete_education_removes_existing_record() -> None:
    education_id = UUID("11111111-1111-1111-1111-111111111111")
    candidate_id = UUID("22222222-2222-2222-2222-222222222222")

    education = CandidateEducation(
        id=education_id,
        candidate_id=candidate_id,
        institution="University",
        degree="MCA",
    )

    repository = FakeCandidateEducationRepository()
    repository.education.append(education)

    await DeleteEducation(repository).execute(education_id)

    assert repository.education == []


@pytest.mark.asyncio
async def test_delete_education_rejects_missing_education() -> None:
    education_id = UUID("11111111-1111-1111-1111-111111111111")

    repository = FakeCandidateEducationRepository()

    with pytest.raises(
        EducationNotFoundError,
        match=f"Education '{education_id}' was not found.",
    ):
        await DeleteEducation(repository).execute(education_id)

    assert repository.education == []
