from dataclasses import dataclass

from packages.domain.evaluation.enums import EvaluationDecision


@dataclass(frozen=True, slots=True)
class SkillScore:
    """Result of comparing candidate skills with required job skills."""

    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


def calculate_skill_score(
    required_skills: tuple[str, ...],
    candidate_skills: tuple[str, ...],
) -> SkillScore:
    """Calculate how closely candidate skills match required skills."""

    candidate_skill_lookup = {
        skill.strip().casefold() for skill in candidate_skills if skill.strip()
    }

    matched_skills = tuple(
        required_skill
        for required_skill in required_skills
        if required_skill.strip().casefold() in candidate_skill_lookup
    )

    missing_skills = tuple(
        required_skill
        for required_skill in required_skills
        if required_skill.strip().casefold() not in candidate_skill_lookup
    )

    if required_skills:
        score = len(matched_skills) / len(required_skills)
    else:
        score = 1.0

    return SkillScore(
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )


def determine_evaluation_decision(
    score: float,
) -> EvaluationDecision:
    """Convert a normalized score into an evaluation decision."""

    if not 0.0 <= score <= 1.0:
        raise ValueError(
            "Evaluation score must be between 0.0 and 1.0.",
        )

    if score >= 0.8:
        return EvaluationDecision.STRONG_MATCH

    if score >= 0.6:
        return EvaluationDecision.MATCH

    if score >= 0.3:
        return EvaluationDecision.WEAK_MATCH

    return EvaluationDecision.NO_MATCH
