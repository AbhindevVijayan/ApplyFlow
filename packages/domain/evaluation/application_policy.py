from packages.domain.evaluation.entities import EvaluationResult
from packages.domain.evaluation.enums import EvaluationDecision


def is_eligible_for_auto_application(
    evaluation: EvaluationResult,
) -> bool:
    """Determine whether a job should be automatically applied to."""

    return evaluation.decision in (
        EvaluationDecision.STRONG_MATCH,
        EvaluationDecision.MATCH,
    )