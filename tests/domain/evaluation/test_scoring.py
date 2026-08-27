import pytest

from packages.domain.evaluation.enums import EvaluationDecision
from packages.domain.evaluation.scoring import (
    calculate_skill_score,
    determine_evaluation_decision,
)


def test_calculate_skill_score_matches_skills_case_insensitively() -> None:
    result = calculate_skill_score(
        required_skills=("Python", "Django"),
        candidate_skills=("python", "django"),
    )

    assert result.score == 1.0
    assert result.matched_skills == ("Python", "Django")
    assert result.missing_skills == ()


def test_calculate_skill_score_returns_missing_skills() -> None:
    result = calculate_skill_score(
        required_skills=("Python", "Django", "FastAPI", "MySQL"),
        candidate_skills=("Python", "Django"),
    )

    assert result.score == 0.5
    assert result.matched_skills == ("Python", "Django")
    assert result.missing_skills == ("FastAPI", "MySQL")


def test_calculate_skill_score_returns_full_score_when_no_skills_required() -> None:
    result = calculate_skill_score(
        required_skills=(),
        candidate_skills=(),
    )

    assert result.score == 1.0
    assert result.matched_skills == ()
    assert result.missing_skills == ()


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (1.0, EvaluationDecision.STRONG_MATCH),
        (0.8, EvaluationDecision.STRONG_MATCH),
        (0.7, EvaluationDecision.MATCH),
        (0.6, EvaluationDecision.MATCH),
        (0.5, EvaluationDecision.WEAK_MATCH),
        (0.3, EvaluationDecision.WEAK_MATCH),
        (0.2, EvaluationDecision.NO_MATCH),
        (0.0, EvaluationDecision.NO_MATCH),
    ],
)
def test_determine_evaluation_decision(
    score: float,
    expected: EvaluationDecision,
) -> None:
    assert determine_evaluation_decision(score) == expected


@pytest.mark.parametrize(
    "score",
    [-0.1, 1.1, 2.0],
)
def test_determine_evaluation_decision_rejects_invalid_score(
    score: float,
) -> None:
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        determine_evaluation_decision(score)
