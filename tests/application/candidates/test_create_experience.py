from datetime import date
from uuid import UUID, uuid4

import pytest

from packages.application.candidates.create_experience import (
    CreateExperience,
    CreateExperienceCommand,
    InvalidExperienceError,
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

    async def delete(self, experience_id: UUID) -> None:
        self.experiences = [
            experience for experience in self.experiences if experience.id != experience_id
        ]


@pytest.mark.asyncio
async def test_create_experience_creates_and_returns_experience() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = CreateExperience(repository)

    candidate_id = uuid4()

    command = CreateExperienceCommand(
        candidate_id=candidate_id,
        company_name="Anjali Bakery",
        job_title="Software Developer",
        employment_type="Full-time",
        location="Kerala, India",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
        description="Developed internal software systems.",
    )

    experience = await use_case.execute(command)

    assert experience.company_name == "Anjali Bakery"
    assert experience.job_title == "Software Developer"
    assert experience.employment_type == "Full-time"
    assert experience.location == "Kerala, India"
    assert experience.start_date == date(2024, 1, 1)
    assert experience.end_date == date(2025, 1, 1)
    assert experience.description == "Developed internal software systems."
    assert experience.is_current is False
    assert experience.candidate_id == candidate_id
    assert isinstance(experience.id, UUID)

    assert repository.experiences == [experience]


@pytest.mark.asyncio
async def test_create_experience_allows_optional_fields_to_be_none() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = CreateExperience(repository)

    command = CreateExperienceCommand(
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Developer",
    )

    experience = await use_case.execute(command)

    assert experience.company_name == "Example Company"
    assert experience.job_title == "Developer"
    assert experience.employment_type is None
    assert experience.location is None
    assert experience.start_date is None
    assert experience.end_date is None
    assert experience.description is None
    assert experience.is_current is False


@pytest.mark.asyncio
async def test_create_experience_rejects_end_date_before_start_date() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = CreateExperience(repository)

    command = CreateExperienceCommand(
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Developer",
        start_date=date(2025, 1, 1),
        end_date=date(2024, 1, 1),
    )

    with pytest.raises(
        InvalidExperienceError,
        match="end_date cannot be earlier than start_date.",
    ):
        await use_case.execute(command)

    assert repository.experiences == []


@pytest.mark.asyncio
async def test_create_experience_rejects_current_with_end_date() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = CreateExperience(repository)

    command = CreateExperienceCommand(
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Developer",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
        is_current=True,
    )

    with pytest.raises(
        InvalidExperienceError,
        match="Current experience cannot have an end_date.",
    ):
        await use_case.execute(command)

    assert repository.experiences == []
