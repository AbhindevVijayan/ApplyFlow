from packages.database.models.resume import Resume as ResumeModel
from packages.domain.resumes.entities import Resume


def to_domain(model: ResumeModel) -> Resume:
    """Convert a database resume into a domain resume."""
    return Resume(
        id=model.id,
        candidate_id=model.candidate_id,
        filename=model.filename,
        content_type=model.content_type,
        storage_key=model.storage_key,
        parsed_text=model.parsed_text,
        is_canonical=model.is_canonical,
        created_at=model.created_at,
    )


def to_model(resume: Resume) -> ResumeModel:
    """Convert a domain resume into a database resume."""
    return ResumeModel(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        content_type=resume.content_type,
        storage_key=resume.storage_key,
        parsed_text=resume.parsed_text,
        is_canonical=resume.is_canonical,
    )
