from datetime import date
from uuid import UUID, uuid4

import pytest

from packages.application.candidates.list_experience import ListExperience
from packages.domain.candidates.experience import CandidateExperience


class FakeCandidateExperienceRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.experiences: list[CandidateExperience] = []

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[CandidateExperience]:
        return [
            experience for experience in self.experiences if experience.candidate_id == candidate_id
        ]


@pytest.mark.asyncio
async def test_list_experience_returns_candidate_experience() -> None:
    repository = FakeCandidateExperienceRepository()

    candidate_id = uuid4()

    older = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Company A",
        job_title="Junior Developer",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 1, 1),
    )

    newer = CandidateExperience(
        id=uuid4(),
        candidate_id=candidate_id,
        company_name="Company B",
        job_title="Software Developer",
        start_date=date(2024, 1, 1),
        is_current=True,
    )

    repository.experiences.extend([older, newer])

    use_case = ListExperience(repository)

    result = await use_case.by_candidate(candidate_id)

    assert len(result) == 2
    assert result == [older, newer]


@pytest.mark.asyncio
async def test_list_experience_returns_empty_list_when_none_exist() -> None:
    repository = FakeCandidateExperienceRepository()
    use_case = ListExperience(repository)

    result = await use_case.by_candidate(uuid4())

    assert result == []
