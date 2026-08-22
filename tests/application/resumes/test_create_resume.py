from uuid import uuid4

import pytest

from packages.application.resumes.create_resume import (
    CreateResume,
    CreateResumeCommand,
)
from packages.domain.resumes.entities import Resume


class FakeResumeRepository:
    def __init__(self) -> None:
        self.resumes: list[Resume] = []

    async def create(self, resume: Resume) -> Resume:
        self.resumes.append(resume)
        return resume

    async def get_by_id(self, resume_id):
        return next(
            (resume for resume in self.resumes if resume.id == resume_id),
            None,
        )

    async def get_by_candidate_id(self, candidate_id):
        return [resume for resume in self.resumes if resume.candidate_id == candidate_id]

    async def get_canonical_by_candidate_id(self, candidate_id):
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

    async def delete(self, resume_id) -> None:
        self.resumes = [resume for resume in self.resumes if resume.id != resume_id]


@pytest.mark.asyncio
async def test_create_resume() -> None:
    repository = FakeResumeRepository()
    use_case = CreateResume(repository)

    candidate_id = uuid4()

    result = await use_case.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="resume.pdf",
            content_type="application/pdf",
            storage_key="resumes/test-resume.pdf",
        ),
    )

    assert result.candidate_id == candidate_id
    assert result.filename == "resume.pdf"
    assert result.content_type == "application/pdf"
    assert result.storage_key == "resumes/test-resume.pdf"
    assert result.parsed_text is None
    assert result.is_canonical is False
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_resume_as_canonical() -> None:
    repository = FakeResumeRepository()
    use_case = CreateResume(repository)

    candidate_id = uuid4()

    result = await use_case.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="primary-resume.pdf",
            content_type="application/pdf",
            storage_key="resumes/primary-resume.pdf",
            is_canonical=True,
        ),
    )

    assert result.candidate_id == candidate_id
    assert result.is_canonical is True


@pytest.mark.asyncio
async def test_create_resume_defaults_to_non_canonical() -> None:
    repository = FakeResumeRepository()
    use_case = CreateResume(repository)

    result = await use_case.execute(
        CreateResumeCommand(
            candidate_id=uuid4(),
            filename="secondary-resume.pdf",
            content_type="application/pdf",
            storage_key="resumes/secondary-resume.pdf",
        ),
    )

    assert result.is_canonical is False


@pytest.mark.asyncio
async def test_create_canonical_resume_replaces_existing_canonical() -> None:
    repository = FakeResumeRepository()
    use_case = CreateResume(repository)

    candidate_id = uuid4()

    first = await use_case.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="first.pdf",
            content_type="application/pdf",
            storage_key="resumes/first.pdf",
            is_canonical=True,
        ),
    )

    second = await use_case.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="second.pdf",
            content_type="application/pdf",
            storage_key="resumes/second.pdf",
            is_canonical=True,
        ),
    )

    stored_first = await repository.get_by_id(first.id)
    stored_second = await repository.get_by_id(second.id)

    assert stored_first is not None
    assert stored_second is not None

    assert stored_first.is_canonical is False
    assert stored_second.is_canonical is True
