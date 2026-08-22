from packages.database.models.candidate import Candidate as CandidateModel
from packages.domain.candidates.entities import Candidate


def to_domain(model: CandidateModel) -> Candidate:
    """Convert a database candidate into a domain candidate."""
    return Candidate(
        id=model.id,
        full_name=model.full_name,
        email=model.email,
        phone=model.phone,
        location=model.location,
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

    return model
