from dataclasses import dataclass
from uuid import UUID

from packages.domain.evaluation.enums import EvaluationDecision


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Result of evaluating a job against a candidate."""

    job_id: UUID
    candidate_id: UUID
    score: float
    decision: EvaluationDecision
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    location_match: bool
    employment_type_match: bool
    reasons: tuple[str, ...]
