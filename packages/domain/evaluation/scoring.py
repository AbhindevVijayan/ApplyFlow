from dataclasses import dataclass

from packages.domain.evaluation.enums import EvaluationDecision


@dataclass(frozen=True, slots=True)
class SkillScore:
    """Result of comparing candidate skills with required job skills."""

    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WeightedScore:
    """Combined evaluation score across available criteria."""

    score: float
    skill_score: float | None
    location_score: float | None
    employment_type_score: float | None


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


def calculate_weighted_score(
    *,
    skill_score: float | None,
    location_score: float | None,
    employment_type_score: float | None,
) -> WeightedScore:
    """Calculate a weighted score using the criteria that are available."""

    weights = {
        "skill": 0.7,
        "location": 0.2,
        "employment_type": 0.1,
    }

    available_scores = {
        "skill": skill_score,
        "location": location_score,
        "employment_type": employment_type_score,
    }

    weighted_total = 0.0
    total_weight = 0.0

    for criterion, criterion_score in available_scores.items():
        if criterion_score is None:
            continue

        if not 0.0 <= criterion_score <= 1.0:
            raise ValueError(
                f"{criterion} score must be between 0.0 and 1.0.",
            )

        weight = weights[criterion]

        weighted_total += criterion_score * weight
        total_weight += weight

    if total_weight == 0.0:
        final_score = 0.0
    else:
        final_score = weighted_total / total_weight

    return WeightedScore(
        score=final_score,
        skill_score=skill_score,
        location_score=location_score,
        employment_type_score=employment_type_score,
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
