from uuid import UUID, uuid4

import pytest

from packages.application.resumes.get_resume import (
    GetResume,
    GetResumeCommand,
)
from packages.domain.resumes.entities import Resume
from packages.domain.resumes.repository import ResumeRepository


class FakeResumeRepository(ResumeRepository):
    def __init__(self, resumes: list[Resume] | None = None) -> None:
        self.resumes = resumes or []

    async def create(self, resume: Resume) -> Resume:
        self.resumes.append(resume)
        return resume

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        return next(
            (resume for resume in self.resumes if resume.id == resume_id),
            None,
        )

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        return [resume for resume in self.resumes if resume.candidate_id == candidate_id]

    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        return next(
            (
                resume
                for resume in self.resumes
                if resume.candidate_id == candidate_id and resume.is_canonical
            ),
            None,
        )

    async def update(self, resume: Resume) -> Resume:
        for index, existing in enumerate(self.resumes):
            if existing.id == resume.id:
                self.resumes[index] = resume
                return resume

        raise AssertionError("Resume not found")

    async def delete(self, resume_id: UUID) -> None:
        self.resumes = [resume for resume in self.resumes if resume.id != resume_id]


def make_resume(
    candidate_id: UUID,
    *,
    is_canonical: bool = False,
) -> Resume:
    return Resume(
        id=uuid4(),
        candidate_id=candidate_id,
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}-resume.pdf",
        parsed_text=None,
        is_canonical=is_canonical,
        created_at=None,
    )


@pytest.mark.asyncio
async def test_get_resume_by_id() -> None:
    candidate_id = uuid4()
    resume = make_resume(candidate_id)

    repository = FakeResumeRepository([resume])
    use_case = GetResume(repository)

    result = await use_case.execute(
        GetResumeCommand(resume_id=resume.id),
    )

    assert result == resume


@pytest.mark.asyncio
async def test_get_resume_by_id_returns_none_when_not_found() -> None:
    repository = FakeResumeRepository()
    use_case = GetResume(repository)

    result = await use_case.execute(
        GetResumeCommand(resume_id=uuid4()),
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_resumes_by_candidate_id() -> None:
    candidate_id = uuid4()

    first = make_resume(candidate_id)
    second = make_resume(candidate_id)

    repository = FakeResumeRepository([first, second])
    use_case = GetResume(repository)

    result = await use_case.execute(
        GetResumeCommand(candidate_id=candidate_id),
    )

    assert result == [first, second]


@pytest.mark.asyncio
async def test_get_canonical_resume_by_candidate_id() -> None:
    candidate_id = uuid4()

    non_canonical = make_resume(candidate_id)
    canonical = make_resume(candidate_id, is_canonical=True)

    repository = FakeResumeRepository(
        [non_canonical, canonical],
    )
    use_case = GetResume(repository)

    result = await use_case.execute(
        GetResumeCommand(
            candidate_id=candidate_id,
            canonical_only=True,
        ),
    )

    assert result == canonical


@pytest.mark.asyncio
async def test_get_canonical_resume_returns_none_when_not_found() -> None:
    candidate_id = uuid4()

    repository = FakeResumeRepository(
        [make_resume(candidate_id)],
    )
    use_case = GetResume(repository)

    result = await use_case.execute(
        GetResumeCommand(
            candidate_id=candidate_id,
            canonical_only=True,
        ),
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_resume_requires_identifier() -> None:
    repository = FakeResumeRepository()
    use_case = GetResume(repository)

    with pytest.raises(
        ValueError,
        match="candidate_id is required when resume_id is not provided",
    ):
        await use_case.execute(
            GetResumeCommand(),
        )
