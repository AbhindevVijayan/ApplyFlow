from datetime import date
from uuid import UUID, uuid4

import pytest

from packages.application.candidates.update_experience import (
    ExperienceNotFoundError,
    InvalidExperienceError,
    UpdateExperience,
    UpdateExperienceCommand,
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

    async def update(
        self,
        experience: CandidateExperience,
    ) -> CandidateExperience:
        for index, existing in enumerate(self.experiences):
            if existing.id == experience.id:
                self.experiences[index] = experience
                return experience

        raise ValueError("Candidate experience not found")

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        return [
            experience for experience in self.experiences if experience.candidate_id == candidate_id
        ]

    async def delete(
        self,
        experience_id: UUID,
    ) -> None:
        self.experiences = [
            experience for experience in self.experiences if experience.id != experience_id
        ]


@pytest.mark.asyncio
async def test_update_experience_updates_fields() -> None:
    repository = FakeCandidateExperienceRepository()

    candidate_id = uuid4()

    existing = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Original Company",
        job_title="Junior Developer",
        employment_type="Full-time",
        location="Kottayam, India",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 1, 1),
        description="Original description.",
        is_current=False,
    )

    await repository.create(existing)

    use_case = UpdateExperience(repository)

    command = UpdateExperienceCommand(
        experience_id=existing.id,
        company_name="Updated Company",
        job_title="Senior Developer",
        employment_type="Contract",
        location="Bengaluru, India",
        start_date=date(2024, 1, 1),
        end_date=None,
        description="Updated professional experience.",
        is_current=True,
    )

    result = await use_case.execute(command)

    assert result.id == existing.id
    assert result.candidate_id == candidate_id
    assert result.company_name == "Updated Company"
    assert result.job_title == "Senior Developer"
    assert result.employment_type == "Contract"
    assert result.location == "Bengaluru, India"
    assert result.start_date == date(2024, 1, 1)
    assert result.end_date is None
    assert result.description == "Updated professional experience."
    assert result.is_current is True

    assert repository.experiences[0] == result


@pytest.mark.asyncio
async def test_update_experience_can_clear_nullable_fields() -> None:
    repository = FakeCandidateExperienceRepository()

    existing = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Original Company",
        job_title="Developer",
        employment_type="Full-time",
        location="Kerala, India",
        start_date=date(2024, 1, 1),
        description="Some description.",
    )

    await repository.create(existing)

    use_case = UpdateExperience(repository)

    command = UpdateExperienceCommand(
        experience_id=existing.id,
        company_name="Updated Company",
        job_title="Developer",
        employment_type=None,
        location=None,
        start_date=None,
        end_date=None,
        description=None,
        is_current=False,
    )

    result = await use_case.execute(command)

    assert result.company_name == "Updated Company"
    assert result.employment_type is None
    assert result.location is None
    assert result.start_date is None
    assert result.end_date is None
    assert result.description is None
    assert result.is_current is False


@pytest.mark.asyncio
async def test_update_experience_rejects_unknown_experience() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = UpdateExperience(repository)

    experience_id = uuid4()

    command = UpdateExperienceCommand(
        experience_id=experience_id,
        company_name="Example Company",
        job_title="Developer",
    )

    with pytest.raises(
        ExperienceNotFoundError,
        match=f"Experience '{experience_id}' was not found.",
    ):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_update_experience_rejects_invalid_dates() -> None:
    repository = FakeCandidateExperienceRepository()

    existing = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Developer",
    )

    await repository.create(existing)

    use_case = UpdateExperience(repository)

    command = UpdateExperienceCommand(
        experience_id=existing.id,
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


@pytest.mark.asyncio
async def test_update_experience_rejects_current_with_end_date() -> None:
    repository = FakeCandidateExperienceRepository()

    existing = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Example Company",
        job_title="Developer",
    )

    await repository.create(existing)

    use_case = UpdateExperience(repository)

    command = UpdateExperienceCommand(
        experience_id=existing.id,
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
