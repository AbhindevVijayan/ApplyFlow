from datetime import date
from uuid import uuid4

import pytest

from packages.domain.candidates.experience import CandidateExperience


def test_candidate_experience_contains_required_fields() -> None:
    candidate_id = uuid4()
    experience_id = uuid4()

    experience = CandidateExperience(
        id=experience_id,
        candidate_id=candidate_id,
        company_name="Acme Technologies",
        job_title="Software Engineer",
    )

    assert experience.id == experience_id
    assert experience.candidate_id == candidate_id
    assert experience.company_name == "Acme Technologies"
    assert experience.job_title == "Software Engineer"


def test_candidate_experience_optional_fields_default_correctly() -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Acme Technologies",
        job_title="Software Engineer",
    )

    assert experience.employment_type is None
    assert experience.location is None
    assert experience.start_date is None
    assert experience.end_date is None
    assert experience.description is None
    assert experience.is_current is False


def test_candidate_experience_contains_all_fields() -> None:
    experience_id = uuid4()
    candidate_id = uuid4()
    start_date = date(2024, 1, 15)
    end_date = date(2026, 1, 31)

    experience = CandidateExperience(
        id=experience_id,
        candidate_id=candidate_id,
        company_name="Acme Technologies",
        job_title="Senior Software Engineer",
        employment_type="Full-time",
        location="Bengaluru, India",
        start_date=start_date,
        end_date=end_date,
        description="Built backend services and internal automation systems.",
        is_current=False,
    )

    assert experience.id == experience_id
    assert experience.candidate_id == candidate_id
    assert experience.company_name == "Acme Technologies"
    assert experience.job_title == "Senior Software Engineer"
    assert experience.employment_type == "Full-time"
    assert experience.location == "Bengaluru, India"
    assert experience.start_date == start_date
    assert experience.end_date == end_date
    assert experience.description == "Built backend services and internal automation systems."
    assert experience.is_current is False


def test_candidate_experience_is_immutable() -> None:
    experience = CandidateExperience(
        id=uuid4(),
        candidate_id=uuid4(),
        company_name="Acme Technologies",
        job_title="Software Engineer",
    )

    with pytest.raises(AttributeError):
        experience.job_title = "Senior Software Engineer"  # type: ignore[misc]
