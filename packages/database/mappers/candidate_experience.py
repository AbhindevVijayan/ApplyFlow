from packages.database.models.candidate_experience import (
    CandidateExperience as CandidateExperienceModel,
)
from packages.domain.candidates.experience import CandidateExperience


def to_domain(
    model: CandidateExperienceModel,
) -> CandidateExperience:
    """Convert a database experience record into a domain entity."""
    return CandidateExperience(
        id=model.id,
        candidate_id=model.candidate_id,
        company_name=model.company_name,
        job_title=model.job_title,
        employment_type=model.employment_type,
        location=model.location,
        start_date=model.start_date,
        end_date=model.end_date,
        description=model.description,
        is_current=model.is_current,
    )


def to_model(
    experience: CandidateExperience,
) -> CandidateExperienceModel:
    """Convert a domain experience entity into a database model."""
    return CandidateExperienceModel(
        id=experience.id,
        candidate_id=experience.candidate_id,
        company_name=experience.company_name,
        job_title=experience.job_title,
        employment_type=experience.employment_type,
        location=experience.location,
        start_date=experience.start_date,
        end_date=experience.end_date,
        description=experience.description,
        is_current=experience.is_current,
    )
