from datetime import date
from uuid import UUID, uuid4

import pytest

from packages.application.candidates.get_experience import (
    ExperienceNotFoundError,
    GetExperience,
)
from packages.domain.candidates.experience import CandidateExperience


class FakeCandidateExperienceRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.experiences: list[CandidateExperience] = []

    async def create(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        self.experiences.append(experience)
        return experience

    async def get_by_id(
        self,
        experience_id: UUID,
    ) -> CandidateExperience | None:
        return next(
            (experience for experience in self.experiences if experience.id == experience_id),
            None,
        )

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        return [
            experience for experience in self.experiences if experience.candidate_id == candidate_id
        ]

    async def update(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        for index, existing in enumerate(self.experiences):
            if existing.id == experience.id:
                self.experiences[index] = experience
                return experience

        raise ValueError("Candidate experience not found")

    async def delete(
        self,
        experience_id: UUID,
    ) -> None:
        self.experiences = [
            experience for experience in self.experiences if experience.id != experience_id
        ]


@pytest.mark.asyncio
async def test_get_experience_returns_existing_experience() -> None:
    repository = FakeCandidateExperienceRepository()

    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Software Developer",
        employment_type="Full-time",
        location="Kerala, India",
        start_date=date(2024, 1, 1),
        description="Developed software systems.",
    )

    await repository.create(experience)

    use_case = GetExperience(repository)

    result = await use_case.execute(experience.id)

    assert result is experience
    assert result.id == experience.id
    assert result.company_name == "Example Company"
    assert result.job_title == "Software Developer"


@pytest.mark.asyncio
async def test_get_experience_rejects_missing_experience() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = GetExperience(repository)

    experience_id = uuid4()

    with pytest.raises(
        ExperienceNotFoundError,
        match=f"Candidate experience '{experience_id}' was not found.",
    ):
        await use_case.execute(experience_id)
