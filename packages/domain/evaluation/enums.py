from enum import StrEnum


class EvaluationDecision(StrEnum):
    """Decision produced by job evaluation."""

    STRONG_MATCH = "strong_match"
    MATCH = "match"
    WEAK_MATCH = "weak_match"
    NO_MATCH = "no_match"
