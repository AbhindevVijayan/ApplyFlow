from datetime import UTC, datetime
from uuid import UUID

from packages.domain.resumes.entities import Resume


def test_resume_contains_required_fields() -> None:
    resume_id = UUID("11111111-1111-1111-1111-111111111111")
    candidate_id = UUID("22222222-2222-2222-2222-222222222222")

    resume = Resume(
        id=resume_id,
        candidate_id=candidate_id,
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resumes/resume.pdf",
    )

    assert resume.id == resume_id
    assert resume.candidate_id == candidate_id
    assert resume.filename == "resume.pdf"
    assert resume.content_type == "application/pdf"
    assert resume.storage_key == "resumes/resume.pdf"


def test_resume_optional_fields_default_correctly() -> None:
    resume = Resume(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        candidate_id=UUID("22222222-2222-2222-2222-222222222222"),
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resumes/resume.pdf",
    )

    assert resume.parsed_text is None
    assert resume.is_canonical is False
    assert resume.created_at is None


def test_resume_accepts_parsed_text_and_created_at() -> None:
    created_at = datetime(
        2026,
        8,
        22,
        10,
        30,
        tzinfo=UTC,
    )

    resume = Resume(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        candidate_id=UUID("22222222-2222-2222-2222-222222222222"),
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resumes/resume.pdf",
        parsed_text="Python developer with FastAPI experience.",
        is_canonical=True,
        created_at=created_at,
    )

    assert resume.parsed_text == "Python developer with FastAPI experience."
    assert resume.is_canonical is True
    assert resume.created_at == created_at
