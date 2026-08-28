from uuid import UUID, uuid4

import pytest

from packages.application.candidates.update_candidate import (
    CandidateEmailAlreadyExistsError,
    CandidateNotFoundError,
    UpdateCandidate,
    UpdateCandidateCommand,
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
async def test_update_candidate_updates_fields() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="Old Name",
        email="old@example.com",
        phone="1234567890",
        location="Kerala",
    )

    await repository.create(candidate)

    use_case = UpdateCandidate(repository)

    updated = await use_case.execute(
        UpdateCandidateCommand(
            candidate_id=candidate.id,
            full_name="New Name",
            email="new@example.com",
            phone="9876543210",
            location="Bangalore",
        ),
    )

    assert updated.id == candidate.id
    assert updated.full_name == "New Name"
    assert updated.email == "new@example.com"
    assert updated.phone == "9876543210"
    assert updated.location == "Bangalore"


@pytest.mark.asyncio
async def test_update_candidate_preserves_unspecified_fields() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="Original Name",
        email="original@example.com",
        phone="1234567890",
        location="Kerala",
    )

    await repository.create(candidate)

    use_case = UpdateCandidate(repository)

    updated = await use_case.execute(
        UpdateCandidateCommand(
            candidate_id=candidate.id,
            full_name="Updated Name",
        ),
    )

    assert updated.id == candidate.id
    assert updated.full_name == "Updated Name"
    assert updated.email == "original@example.com"
    assert updated.phone == "1234567890"
    assert updated.location == "Kerala"


@pytest.mark.asyncio
async def test_update_candidate_rejects_unknown_candidate() -> None:
    repository = FakeCandidateRepository()

    use_case = UpdateCandidate(repository)

    candidate_id = uuid4()

    with pytest.raises(CandidateNotFoundError):
        await use_case.execute(
            UpdateCandidateCommand(
                candidate_id=candidate_id,
                full_name="New Name",
            ),
        )


@pytest.mark.asyncio
async def test_update_candidate_rejects_duplicate_email() -> None:
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

    use_case = UpdateCandidate(repository)

    with pytest.raises(CandidateEmailAlreadyExistsError):
        await use_case.execute(
            UpdateCandidateCommand(
                candidate_id=first.id,
                email="second@example.com",
            ),
        )


@pytest.mark.asyncio
async def test_update_candidate_can_clear_nullable_fields() -> None:
    repository = FakeCandidateRepository()

    candidate = Candidate(
        id=uuid4(),
        full_name="Clear Fields Candidate",
        email="clear-fields@example.com",
        phone="9876543210",
        location="Kerala",
    )

    await repository.create(candidate)

    use_case = UpdateCandidate(repository)

    updated = await use_case.execute(
        UpdateCandidateCommand(
            candidate_id=candidate.id,
            phone=None,
            location=None,
        ),
    )

    assert updated.id == candidate.id
    assert updated.full_name == "Clear Fields Candidate"
    assert updated.email == "clear-fields@example.com"
    assert updated.phone is None
    assert updated.location is None
