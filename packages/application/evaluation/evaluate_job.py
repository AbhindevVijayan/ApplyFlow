from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.evaluation.entities import EvaluationResult
from packages.domain.evaluation.scoring import (
    calculate_skill_score,
    calculate_weighted_score,
    determine_evaluation_decision,
)
from packages.domain.jobs.repositories import JobRepository
from packages.domain.skills.repository import SkillRepository


class JobNotFoundError(Exception):
    """Raised when the requested job does not exist."""


class CandidateNotFoundError(Exception):
    """Raised when the requested candidate does not exist."""


class EvaluateJob:
    """Evaluate how well a candidate matches a job."""

    def __init__(
        self,
        job_repository: JobRepository,
        candidate_repository: CandidateRepository,
        skill_repository: SkillRepository,
    ) -> None:
        self._job_repository = job_repository
        self._candidate_repository = candidate_repository
        self._skill_repository = skill_repository

    async def execute(
        self,
        candidate_id: UUID,
        job_id: UUID,
    ) -> EvaluationResult:
        """Evaluate a candidate against a job."""

        job = await self._job_repository.get_by_id(job_id)

        if job is None:
            raise JobNotFoundError(
                f"Job '{job_id}' was not found.",
            )

        candidate = await self._candidate_repository.get_by_id(
            candidate_id,
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate '{candidate_id}' was not found.",
            )

        candidate_skills = await self._skill_repository.get_candidate_skills(
            candidate_id,
        )

        candidate_skill_names: list[str] = []

        for candidate_skill in candidate_skills:
            skill = await self._skill_repository.get_by_id(
                candidate_skill.skill_id,
            )

            if skill is not None:
                candidate_skill_names.append(skill.name)

        skill_result = calculate_skill_score(
            required_skills=job.required_skills,
            candidate_skills=tuple(candidate_skill_names),
        )

        location_match = self._location_matches(
            candidate.location,
            job.location,
        )

        employment_type_match = self._employment_type_matches(
            job.employment_type,
        )

        location_score = 1.0 if location_match is True else 0.0 if location_match is False else None

        employment_type_score = (
            1.0
            if employment_type_match is True
            else 0.0
            if employment_type_match is False
            else None
        )

        skill_score = skill_result.score if job.required_skills else None

        evaluation_score = calculate_weighted_score(
            skill_score=skill_score,
            location_score=location_score,
            employment_type_score=employment_type_score,
        )

        score = evaluation_score.score
        
        decision_score = (
            skill_result.score
            if job.required_skills
            else score
        )
                
        decision = determine_evaluation_decision(
            decision_score,
            )
        
        reasons = self._build_reasons(
            matched_skills=skill_result.matched_skills,
            missing_skills=skill_result.missing_skills,
            location_match=location_match,
            employment_type_match=employment_type_match,
        )

        return EvaluationResult(
            job_id=job_id,
            candidate_id=candidate_id,
            score=score,
            decision=decision,
            skill_score=evaluation_score.skill_score,
            location_score=evaluation_score.location_score,
            employment_type_score=evaluation_score.employment_type_score,
            matched_skills=skill_result.matched_skills,
            missing_skills=skill_result.missing_skills,
            location_match=location_match,
            employment_type_match=employment_type_match,
            reasons=reasons,
        )

    @staticmethod
    def _location_matches(
        candidate_location: str | None,
        job_location: str | None,
    ) -> bool | None:
        """Determine whether candidate and job locations are compatible."""

        if job_location is None or not job_location.strip():
            return None

        normalized_job_location = job_location.strip().casefold()

        if normalized_job_location == "remote":
            return True

        if candidate_location is None or not candidate_location.strip():
            return None

        normalized_candidate_location = candidate_location.strip().casefold()

        return normalized_candidate_location == normalized_job_location

    @staticmethod
    def _employment_type_matches(
        job_employment_type: str | None,
        ) -> bool | None:
        """Employment compatibility requires candidate preferences."""
        return None

    @staticmethod
    def _build_reasons(
        *,
        matched_skills: tuple[str, ...],
        missing_skills: tuple[str, ...],
        location_match: bool | None,
        employment_type_match: bool | None,
    ) -> tuple[str, ...]:
        """Build human-readable explanations for the evaluation."""

        reasons: list[str] = []

        total_skills = len(matched_skills) + len(missing_skills)

        if total_skills > 0:
            reasons.append(
                f"{len(matched_skills)} of {total_skills} required skills matched.",
            )

        if missing_skills:
            reasons.append(
                f"Missing required skills: {', '.join(missing_skills)}.",
            )

        if location_match is True:
            reasons.append(
                "Location requirements are compatible.",
            )
        elif location_match is False:
            reasons.append(
                "Location requirements are not compatible.",
            )

        return tuple(reasons)
