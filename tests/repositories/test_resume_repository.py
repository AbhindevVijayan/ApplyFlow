from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.models.resume import Resume
from packages.database.repositories.resume import ResumeRepository
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def candidate(session: AsyncSession) -> Candidate:
    candidate = Candidate(
        full_name="Resume Test Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    return candidate


@pytest.mark.asyncio
async def test_create_and_get_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    resume = Resume(
        candidate_id=candidate.id,
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
        parsed_text="Python developer with experience in FastAPI.",
    )

    created = await repository.create(resume)
    await session.commit()

    assert created.id is not None
    assert created.filename == "resume.pdf"
    assert created.candidate_id == candidate.id

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.storage_key == created.storage_key

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_candidate_id(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    first = Resume(
        candidate_id=candidate.id,
        filename="resume-1.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    second = Resume(
        candidate_id=candidate.id,
        filename="resume-2.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    await repository.create(first)
    await repository.create(second)
    await session.commit()

    resumes = await repository.get_by_candidate_id(candidate.id)

    assert len(resumes) == 2
    assert {resume.id for resume in resumes} == {
        first.id,
        second.id,
    }

    await repository.delete(first)
    await repository.delete(second)
    await session.commit()


@pytest.mark.asyncio
async def test_get_by_candidate_id_returns_empty_list_for_unknown_candidate(
    session: AsyncSession,
) -> None:
    repository = ResumeRepository(session)

    resumes = await repository.get_by_candidate_id(uuid4())

    assert resumes == []


@pytest.mark.asyncio
async def test_get_canonical_by_candidate_id(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    non_canonical = Resume(
        candidate_id=candidate.id,
        filename="old-resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
        is_canonical=False,
    )

    canonical = Resume(
        candidate_id=candidate.id,
        filename="current-resume.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
        is_canonical=True,
    )

    await repository.create(non_canonical)
    await repository.create(canonical)
    await session.commit()

    fetched = await repository.get_canonical_by_candidate_id(
        candidate.id,
    )

    assert fetched is not None
    assert fetched.id == canonical.id
    assert fetched.is_canonical is True

    await repository.delete(non_canonical)
    await repository.delete(canonical)
    await session.commit()


@pytest.mark.asyncio
async def test_update_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    resume = Resume(
        candidate_id=candidate.id,
        filename="original.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    await repository.create(resume)
    await session.commit()

    resume.filename = "updated.pdf"
    resume.parsed_text = "Updated parsed resume content."
    resume.is_canonical = True

    updated = await repository.update(resume)
    await session.commit()

    assert updated.filename == "updated.pdf"
    assert updated.parsed_text == "Updated parsed resume content."
    assert updated.is_canonical is True

    fetched = await repository.get_by_id(resume.id)

    assert fetched is not None
    assert fetched.filename == "updated.pdf"
    assert fetched.is_canonical is True

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_resume(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    resume = Resume(
        candidate_id=candidate.id,
        filename="delete-test.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    await repository.create(resume)
    await session.commit()

    resume_id = resume.id

    fetched = await repository.get_by_id(resume_id)

    assert fetched is not None

    await repository.delete(fetched)
    await session.commit()

    deleted = await repository.get_by_id(resume_id)

    assert deleted is None


@pytest.mark.asyncio
async def test_duplicate_storage_key_raises_integrity_error(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = ResumeRepository(session)

    storage_key = f"resumes/{uuid4()}.pdf"

    first = Resume(
        candidate_id=candidate.id,
        filename="first.pdf",
        content_type="application/pdf",
        storage_key=storage_key,
    )

    second = Resume(
        candidate_id=candidate.id,
        filename="second.pdf",
        content_type="application/pdf",
        storage_key=storage_key,
    )

    await repository.create(first)
    await session.commit()

    first_id = first.id

    with pytest.raises(IntegrityError):
        await repository.create(second)

    await session.rollback()

    existing = await repository.get_by_id(first_id)

    assert existing is not None
    assert existing.id == first.id

    await repository.delete(existing)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_candidate_cascades_to_resumes(
    session: AsyncSession,
) -> None:
    candidate = Candidate(
        full_name="Cascade Test Candidate",
        email=f"{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()

    repository = ResumeRepository(session)

    first = Resume(
        candidate_id=candidate.id,
        filename="resume-1.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    second = Resume(
        candidate_id=candidate.id,
        filename="resume-2.pdf",
        content_type="application/pdf",
        storage_key=f"resumes/{uuid4()}.pdf",
    )

    await repository.create(first)
    await repository.create(second)
    await session.commit()

    first_id = first.id
    second_id = second.id

    await session.delete(candidate)
    await session.commit()

    assert await repository.get_by_id(first_id) is None
    assert await repository.get_by_id(second_id) is None
