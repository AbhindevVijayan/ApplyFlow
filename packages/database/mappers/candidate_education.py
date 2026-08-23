from packages.database.models.candidate_education import (
    CandidateEducation as CandidateEducationModel,
)
from packages.domain.candidates.education import CandidateEducation


def to_domain(
    model: CandidateEducationModel,
) -> CandidateEducation:
    """Convert a database education record into a domain entity."""
    return CandidateEducation(
        id=model.id,
        candidate_id=model.candidate_id,
        institution=model.institution,
        degree=model.degree,
        field_of_study=model.field_of_study,
        start_date=model.start_date,
        end_date=model.end_date,
        grade=model.grade,
        is_current=model.is_current,
    )


def to_model(
    education: CandidateEducation,
) -> CandidateEducationModel:
    """Convert a domain education entity into a database model."""
    return CandidateEducationModel(
        id=education.id,
        candidate_id=education.candidate_id,
        institution=education.institution,
        degree=education.degree,
        field_of_study=education.field_of_study,
        start_date=education.start_date,
        end_date=education.end_date,
        grade=education.grade,
        is_current=education.is_current,
    )