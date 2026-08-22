from uuid import uuid4

import pytest

from packages.application.resumes.create_resume import (
    CreateResume,
    CreateResumeCommand,
)
from packages.application.resumes.update_resume import (
    UpdateResume,
    UpdateResumeCommand,
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
async def test_update_resume() -> None:
    repository = FakeResumeRepository()

    create_resume = CreateResume(repository)
    update_resume = UpdateResume(repository)

    created = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=uuid4(),
            filename="original.pdf",
            content_type="application/pdf",
            storage_key="resumes/original.pdf",
            parsed_text="Original text",
        ),
    )

    updated = await update_resume.execute(
        UpdateResumeCommand(
            resume_id=created.id,
            filename="updated.pdf",
            content_type="application/pdf",
            storage_key="resumes/updated.pdf",
            parsed_text="Updated text",
            is_canonical=True,
        ),
    )

    assert updated.id == created.id
    assert updated.candidate_id == created.candidate_id
    assert updated.filename == "updated.pdf"
    assert updated.content_type == "application/pdf"
    assert updated.storage_key == "resumes/updated.pdf"
    assert updated.parsed_text == "Updated text"
    assert updated.is_canonical is True


@pytest.mark.asyncio
async def test_update_resume_preserves_created_at() -> None:
    repository = FakeResumeRepository()

    create_resume = CreateResume(repository)
    update_resume = UpdateResume(repository)

    created = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=uuid4(),
            filename="original.pdf",
            content_type="application/pdf",
            storage_key="resumes/original.pdf",
        ),
    )

    updated = await update_resume.execute(
        UpdateResumeCommand(
            resume_id=created.id,
            filename="updated.pdf",
            content_type="application/pdf",
            storage_key="resumes/updated.pdf",
        ),
    )

    assert updated.created_at == created.created_at


@pytest.mark.asyncio
async def test_update_canonical_resume_demotes_existing_canonical() -> None:
    repository = FakeResumeRepository()

    create_resume = CreateResume(repository)
    update_resume = UpdateResume(repository)

    candidate_id = uuid4()

    first = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="first.pdf",
            content_type="application/pdf",
            storage_key="resumes/first.pdf",
            is_canonical=True,
        ),
    )

    second = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=candidate_id,
            filename="second.pdf",
            content_type="application/pdf",
            storage_key="resumes/second.pdf",
        ),
    )

    updated = await update_resume.execute(
        UpdateResumeCommand(
            resume_id=second.id,
            filename="second-updated.pdf",
            content_type="application/pdf",
            storage_key="resumes/second-updated.pdf",
            is_canonical=True,
        ),
    )

    stored_first = await repository.get_by_id(first.id)
    stored_second = await repository.get_by_id(second.id)

    assert stored_first is not None
    assert stored_second is not None

    assert stored_first.is_canonical is False
    assert stored_second.is_canonical is True
    assert updated.is_canonical is True


@pytest.mark.asyncio
async def test_update_resume_raises_when_not_found() -> None:
    repository = FakeResumeRepository()
    update_resume = UpdateResume(repository)

    with pytest.raises(ValueError, match="not found"):
        await update_resume.execute(
            UpdateResumeCommand(
                resume_id=uuid4(),
                filename="missing.pdf",
                content_type="application/pdf",
                storage_key="resumes/missing.pdf",
            ),
        )
