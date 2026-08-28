from uuid import UUID, uuid4

import pytest

from packages.application.candidates.get_candidate import (
    CandidateNotFoundError,
    GetCandidate,
)
from packages.domain.candidates.entities import Candidate


class FakeCandidateRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.candidates: dict[UUID, Candidate] = {}

    async def create(self, candidate: Candidate) -> Candidate:
        self.candidates[candidate.id] = candidate
        return candidate

    async def get_by_id(
        self,
        candidate_id: UUID,
    ) -> Candidate | None:
        return self.candidates.get(candidate_id)

    async def get_by_email(
        self,
        email: str,
    ) -> Candidate | None:
        for candidate in self.candidates.values():
            if candidate.email == email:
                return candidate

        return None

    async def update(self, candidate: Candidate) -> Candidate:
        if candidate.id not in self.candidates:
            raise ValueError(f"Candidate not found: {candidate.id}")

        self.candidates[candidate.id] = candidate
        return candidate

    async def list_all(self) -> list[Candidate]:
        return list(self.candidates.values())

    async def delete(
        self,
        candidate_id: UUID,
    ) -> None:
        self.candidates.pop(candidate_id, None)


@pytest.mark.asyncio
async def test_get_candidate_returns_existing_candidate() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        location="Kerala",
    )

    await repository.create(candidate)

    use_case = GetCandidate(repository)

    result = await use_case.execute(candidate.id)

    assert result is candidate
    assert result.id == candidate.id
    assert result.full_name == "John Doe"
    assert result.email == "john@example.com"


@pytest.mark.asyncio
async def test_get_candidate_rejects_unknown_candidate() -> None:
    repository = FakeCandidateRepository()

    use_case = GetCandidate(repository)

    candidate_id = uuid4()

    with pytest.raises(CandidateNotFoundError):
        await use_case.execute(candidate_id)


@pytest.mark.asyncio
async def test_get_candidate_does_not_modify_repository() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="Read Only Candidate",
        email="readonly@example.com",
    )

    await repository.create(candidate)

    use_case = GetCandidate(repository)

    result = await use_case.execute(candidate.id)

    assert result == candidate
    assert len(repository.candidates) == 1
    assert repository.candidates[candidate.id] == candidate
