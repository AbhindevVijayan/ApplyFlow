from uuid import uuid4

import pytest

from packages.application.candidates.delete_candidate import (
    CandidateNotFoundError,
    DeleteCandidate,
)
from packages.domain.candidates.entities import Candidate


class FakeCandidateRepository:
    def __init__(self) -> None:
        self.candidates: dict = {}
        self.deleted_ids: list = []

    async def create(self, candidate: Candidate) -> Candidate:
        self.candidates[candidate.id] = candidate
        return candidate

    async def get_by_id(self, candidate_id):
        return self.candidates.get(candidate_id)

    async def get_by_email(self, email: str):
        for candidate in self.candidates.values():
            if candidate.email == email:
                return candidate

        return None

    async def update(self, candidate: Candidate) -> Candidate:
        self.candidates[candidate.id] = candidate
        return candidate

    async def delete(self, candidate_id) -> None:
        self.deleted_ids.append(candidate_id)
        self.candidates.pop(candidate_id, None)


@pytest.mark.asyncio
async def test_delete_candidate_removes_existing_candidate() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="Delete Candidate",
        email="delete@example.com",
    )

    await repository.create(candidate)

    use_case = DeleteCandidate(repository)

    await use_case.execute(candidate.id)

    assert candidate.id not in repository.candidates
    assert repository.deleted_ids == [candidate.id]


@pytest.mark.asyncio
async def test_delete_candidate_rejects_unknown_candidate() -> None:
    repository = FakeCandidateRepository()

    use_case = DeleteCandidate(repository)

    candidate_id = uuid4()

    with pytest.raises(CandidateNotFoundError):
        await use_case.execute(candidate_id)

    assert repository.deleted_ids == []


@pytest.mark.asyncio
async def test_delete_candidate_only_deletes_requested_candidate() -> None:
    repository = FakeCandidateRepository()

    first = Candidate(
        id=uuid4(),
        full_name="First Candidate",
        email="first@example.com",
    )

    second = Candidate(
        id=uuid4(),
        full_name="Second Candidate",
        email="second@example.com",
    )

    await repository.create(first)
    await repository.create(second)

    use_case = DeleteCandidate(repository)

    await use_case.execute(first.id)

    assert first.id not in repository.candidates
    assert second.id in repository.candidates
    assert repository.deleted_ids == [first.id]
