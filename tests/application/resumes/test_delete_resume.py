from uuid import uuid4

import pytest

from packages.application.resumes.create_resume import (
    CreateResume,
    CreateResumeCommand,
)
from packages.application.resumes.delete_resume import DeleteResume
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
async def test_delete_resume() -> None:
    repository = FakeResumeRepository()

    create_resume = CreateResume(repository)
    delete_resume = DeleteResume(repository)

    created = await create_resume.execute(
        CreateResumeCommand(
            candidate_id=uuid4(),
            filename="delete-me.pdf",
            content_type="application/pdf",
            storage_key="resumes/delete-me.pdf",
        ),
    )

    assert await repository.get_by_id(created.id) is not None

    await delete_resume.execute(created.id)

    assert await repository.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_resume_is_safe_when_resume_does_not_exist() -> None:
    repository = FakeResumeRepository()
    delete_resume = DeleteResume(repository)

    await delete_resume.execute(uuid4())

    assert repository.resumes == []
