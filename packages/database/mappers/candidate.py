from uuid import UUID

from packages.database.models.candidate import Candidate as CandidateModel
from packages.database.models.candidate_profile import (
    CandidateProfile as CandidateProfileModel,
)
from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.profile import CandidateProfile


def profile_to_domain(
    model: CandidateProfileModel,
) -> CandidateProfile:
    """Convert a database candidate profile into a domain profile."""
    return CandidateProfile(
        headline=model.headline,
        summary=model.summary,
        years_of_experience=model.years_of_experience,
        current_job_title=model.current_job_title,
        current_company=model.current_company,
        current_salary=model.current_salary,
        expected_salary=model.expected_salary,
        notice_period_days=model.notice_period_days,
        highest_qualification=model.highest_qualification,
        career_level=model.career_level,
        work_authorization=model.work_authorization,
        willing_to_relocate=model.willing_to_relocate,
        remote_preference=model.remote_preference,
    )


def profile_to_model(
    profile: CandidateProfile,
    candidate_id: UUID,
) -> CandidateProfileModel:
    """Convert a domain profile into a database profile."""
    return CandidateProfileModel(
        candidate_id=candidate_id,
        headline=profile.headline,
        summary=profile.summary,
        years_of_experience=profile.years_of_experience,
        current_job_title=profile.current_job_title,
        current_company=profile.current_company,
        current_salary=profile.current_salary,
        expected_salary=profile.expected_salary,
        notice_period_days=profile.notice_period_days,
        highest_qualification=profile.highest_qualification,
        career_level=profile.career_level,
        work_authorization=profile.work_authorization,
        willing_to_relocate=profile.willing_to_relocate,
        remote_preference=profile.remote_preference,
    )


def to_domain(model: CandidateModel) -> Candidate:
    """Convert a database candidate into a domain candidate."""
    profile = model.profile

    return Candidate(
        id=model.id,
        full_name=model.full_name,
        email=model.email,
        phone=model.phone,
        location=model.location,
        profile=(profile_to_domain(profile) if profile is not None else None),
    )


def to_model(candidate: Candidate) -> CandidateModel:
    """Convert a domain candidate into a database candidate."""
    model = CandidateModel(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
    )

    if candidate.profile is not None:
        model.profile = profile_to_model(
            candidate.profile,
            candidate.id,
        )

    return model
