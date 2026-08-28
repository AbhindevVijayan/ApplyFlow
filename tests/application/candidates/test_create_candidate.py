from uuid import UUID

import pytest

from packages.application.candidates.create_candidate import (
    CandidateAlreadyExistsError,
    CreateCandidate,
    CreateCandidateCommand,
)
from packages.domain.candidates.entities import Candidate


class FakeCandidateRepository:
    """In-memory repository for application-layer tests."""

    def __init__(self) -> None:
        self.candidates: list[Candidate] = []

    async def create(self, candidate: Candidate) -> Candidate:
        self.candidates.append(candidate)
        return candidate

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        return next(
            (candidate for candidate in self.candidates if candidate.id == candidate_id),
            None,
        )

    async def get_by_email(self, email: str) -> Candidate | None:
        return next(
            (candidate for candidate in self.candidates if candidate.email == email),
            None,
        )

    async def update(self, candidate: Candidate) -> Candidate:
        for index, existing in enumerate(self.candidates):
            if existing.id == candidate.id:
                self.candidates[index] = candidate
                return candidate

        raise ValueError("Candidate not found")

    async def list_all(self) -> list[Candidate]:
        return list(self.candidates)

    async def delete(self, candidate_id: UUID) -> None:
        self.candidates = [
            candidate for candidate in self.candidates if candidate.id != candidate_id
        ]


@pytest.mark.asyncio
async def test_create_candidate_creates_and_returns_candidate() -> None:
    repository = FakeCandidateRepository()
    use_case = CreateCandidate(repository)

    command = CreateCandidateCommand(
        full_name="John Doe",
        email="john@example.com",
        phone="9876543210",
        location="Kerala",
    )

    candidate = await use_case.execute(command)

    assert candidate.full_name == "John Doe"
    assert candidate.email == "john@example.com"
    assert candidate.phone == "9876543210"
    assert candidate.location == "Kerala"
    assert candidate.id is not None
    assert isinstance(candidate.id, UUID)

    assert repository.candidates == [candidate]


@pytest.mark.asyncio
async def test_create_candidate_allows_optional_fields_to_be_none() -> None:
    repository = FakeCandidateRepository()
    use_case = CreateCandidate(repository)

    command = CreateCandidateCommand(
        full_name="Jane Doe",
        email="jane@example.com",
    )

    candidate = await use_case.execute(command)

    assert candidate.full_name == "Jane Doe"
    assert candidate.email == "jane@example.com"
    assert candidate.phone is None
    assert candidate.location is None


@pytest.mark.asyncio
async def test_create_candidate_rejects_existing_email() -> None:
    repository = FakeCandidateRepository()

    existing = Candidate(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        full_name="Existing Candidate",
        email="existing@example.com",
    )

    repository.candidates.append(existing)

    use_case = CreateCandidate(repository)

    command = CreateCandidateCommand(
        full_name="Another Candidate",
        email="existing@example.com",
    )

    with pytest.raises(
        CandidateAlreadyExistsError,
        match="Candidate with email 'existing@example.com' already exists.",
    ):
        await use_case.execute(command)

    assert repository.candidates == [existing]
