from datetime import date
from uuid import uuid4

from packages.database.mappers.candidate_education import (
    to_domain,
    to_model,
)
from packages.database.models.candidate_education import CandidateEducation
from packages.domain.candidates.education import CandidateEducation as DomainCandidateEducation


def test_to_domain_maps_all_fields() -> None:
    education_id = uuid4()
    candidate_id = uuid4()

    model = CandidateEducation(
        id=education_id,
        candidate_id=candidate_id,
        institution="University of Kerala",
        degree="Master of Computer Applications",
        field_of_study="Computer Science",
        start_date=date(2023, 1, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
        is_current=False,
    )

    result = to_domain(model)

    assert result.id == education_id
    assert result.candidate_id == candidate_id
    assert result.institution == "University of Kerala"
    assert result.degree == "Master of Computer Applications"
    assert result.field_of_study == "Computer Science"
    assert result.start_date == date(2023, 1, 1)
    assert result.end_date == date(2025, 5, 31)
    assert result.grade == "8.2 CGPA"
    assert result.is_current is False


def test_to_model_maps_domain_education() -> None:
    education_id = uuid4()
    candidate_id = uuid4()

    education = DomainCandidateEducation(
        id=education_id,
        candidate_id=candidate_id,
        institution="University of Kerala",
        degree="Master of Computer Applications",
        field_of_study="Computer Science",
        start_date=date(2023, 1, 1),
        end_date=date(2025, 5, 31),
        grade="8.2 CGPA",
        is_current=False,
    )

    result = to_model(education)

    assert result.id == education_id
    assert result.candidate_id == candidate_id
    assert result.institution == "University of Kerala"
    assert result.degree == "Master of Computer Applications"
    assert result.field_of_study == "Computer Science"
    assert result.start_date == date(2023, 1, 1)
    assert result.end_date == date(2025, 5, 31)
    assert result.grade == "8.2 CGPA"
    assert result.is_current is False
