from uuid import uuid4

import pytest

from packages.domain.evaluation.application_policy import (
    is_eligible_for_auto_application,
)
from packages.domain.evaluation.entities import EvaluationResult
from packages.domain.evaluation.enums import EvaluationDecision


@pytest.mark.parametrize(
    ("decision", "expected"),
    [
        (EvaluationDecision.STRONG_MATCH, True),
        (EvaluationDecision.MATCH, True),
        (EvaluationDecision.WEAK_MATCH, False),
        (EvaluationDecision.NO_MATCH, False),
    ],
)
def test_auto_application_eligibility(
    decision: EvaluationDecision,
    expected: bool,
) -> None:
    evaluation = EvaluationResult(
        job_id=uuid4(),
        candidate_id=uuid4(),
        score=0.75,
        decision=decision,
        skill_score=0.75,
        location_score=1.0,
        employment_type_score=None,
        matched_skills=("Python",),
        missing_skills=(),
        location_match=True,
        employment_type_match=None,
        reasons=(),
    )

    assert is_eligible_for_auto_application(evaluation) is expected
