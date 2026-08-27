from uuid import UUID

from packages.domain.candidates.repository import CandidateRepository
from packages.domain.evaluation.entities import EvaluationResult
from packages.domain.evaluation.scoring import (
    calculate_skill_score,
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

        skill_score = calculate_skill_score(
            required_skills=job.required_skills,
            candidate_skills=tuple(candidate_skill_names),
        )

        score = skill_score.score
        matched_skills = skill_score.matched_skills
        missing_skills = skill_score.missing_skills

        decision = determine_evaluation_decision(score)

        location_match = self._location_matches(
            candidate.location,
            job.location,
        )

        employment_type_match = True

        reasons = (f"{len(matched_skills)} of {len(job.required_skills)} required skills matched.",)

        return EvaluationResult(
            job_id=job_id,
            candidate_id=candidate_id,
            score=score,
            decision=decision,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            location_match=location_match,
            employment_type_match=employment_type_match,
            reasons=reasons,
        )

    @staticmethod
    def _location_matches(
        candidate_location: str | None,
        job_location: str | None,
    ) -> bool:
        """Determine whether candidate and job locations are compatible."""

        if candidate_location is None or job_location is None:
            return False

        candidate = candidate_location.strip().lower()
        job = job_location.strip().lower()

        return candidate == job or job == "remote"
