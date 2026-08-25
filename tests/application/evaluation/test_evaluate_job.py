from datetime import UTC, datetime
from uuid import uuid4

import pytest

from packages.application.evaluation.evaluate_job import (
    CandidateNotFoundError,
    EvaluateJob,
)
from packages.domain.candidates.entities import Candidate
from packages.domain.evaluation.enums import EvaluationDecision
from packages.domain.jobs.entities import Job
from packages.domain.skills.entities import CandidateSkill, Skill


class FakeJobRepository:
    def __init__(self, job: Job) -> None:
        self.job = job

    async def get_by_id(self, job_id):
        if job_id == self.job.id:
            return self.job
        return None


class FakeCandidateRepository:
    def __init__(self, candidate: Candidate) -> None:
        self.candidate = candidate

    async def get_by_id(self, candidate_id):
        if candidate_id == self.candidate.id:
            return self.candidate
        return None


class FakeSkillRepository:
    def __init__(
        self,
        skills: list[Skill],
        candidate_skills: list[CandidateSkill],
    ) -> None:
        self.skills = skills
        self.candidate_skills = candidate_skills

    async def get_candidate_skills(self, candidate_id):
        return [
            assignment
            for assignment in self.candidate_skills
            if assignment.candidate_id == candidate_id
        ]

    async def get_by_id(self, skill_id):
        return next(
            (skill for skill in self.skills if skill.id == skill_id),
            None,
        )


@pytest.mark.asyncio
async def test_evaluate_job_returns_strong_match_for_matching_skills() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    python_id = uuid4()
    django_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    job = Job(
        id=job_id,
        company="Acme",
        title="Python Backend Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/1",
        description=("We are looking for a Python and Django developer to build backend services."),
        location="Remote",
        employment_type="Full-time",
        required_skills=(
            "Python",
            "Django",
        ),
        discovered_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    skills = [
        Skill(id=python_id, name="Python"),
        Skill(id=django_id, name="Django"),
    ]

    candidate_skills = [
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=python_id,
            proficiency="advanced",
        ),
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=django_id,
            proficiency="intermediate",
        ),
    ]

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=skills,
            candidate_skills=candidate_skills,
        ),
    )

    result = await use_case.execute(
        candidate_id=candidate_id,
        job_id=job_id,
    )

    assert result.job_id == job_id
    assert result.candidate_id == candidate_id
    assert result.score == 1.0
    assert result.decision == EvaluationDecision.STRONG_MATCH

    assert result.matched_skills == (
        "Python",
        "Django",
    )

    assert result.missing_skills == ()

    assert result.location_match is True
    assert result.employment_type_match is True


@pytest.mark.asyncio
async def test_evaluate_job_returns_weak_match_for_partial_skills() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    python_id = uuid4()
    django_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    job = Job(
        id=job_id,
        company="Acme",
        title="Backend Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/2",
        required_skills=(
            "Python",
            "Django",
            "FastAPI",
            "MySQL",
        ),
        location="Remote",
        employment_type="Full-time",
    )

    skills = [
        Skill(id=python_id, name="Python"),
        Skill(id=django_id, name="Django"),
    ]

    candidate_skills = [
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=python_id,
            proficiency="advanced",
        ),
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=django_id,
            proficiency="intermediate",
        ),
    ]

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=skills,
            candidate_skills=candidate_skills,
        ),
    )

    result = await use_case.execute(
        candidate_id=candidate_id,
        job_id=job_id,
    )

    assert result.score == 0.5
    assert result.decision == EvaluationDecision.WEAK_MATCH

    assert result.matched_skills == (
        "Python",
        "Django",
    )

    assert result.missing_skills == (
        "FastAPI",
        "MySQL",
    )


@pytest.mark.asyncio
async def test_evaluate_job_matches_skills_case_insensitively() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    python_id = uuid4()
    django_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    job = Job(
        id=job_id,
        company="Acme",
        title="Python Backend Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/4",
        required_skills=(
            " Python ",
            "DJANGO",
        ),
        location="Remote",
        employment_type="Full-time",
    )

    skills = [
        Skill(id=python_id, name="python"),
        Skill(id=django_id, name=" Django "),
    ]

    candidate_skills = [
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=python_id,
            proficiency="advanced",
        ),
        CandidateSkill(
            candidate_id=candidate_id,
            skill_id=django_id,
            proficiency="intermediate",
        ),
    ]

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=skills,
            candidate_skills=candidate_skills,
        ),
    )

    result = await use_case.execute(
        candidate_id=candidate_id,
        job_id=job_id,
    )

    assert result.score == 1.0
    assert result.decision == EvaluationDecision.STRONG_MATCH

    assert result.matched_skills == (
        " Python ",
        "DJANGO",
    )

    assert result.missing_skills == ()


@pytest.mark.asyncio
async def test_evaluate_job_returns_strong_match_when_no_skills_are_required() -> None:
    candidate_id = uuid4()
    job_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    job = Job(
        id=job_id,
        company="Acme",
        title="Software Engineer",
        source="greenhouse",
        source_url="https://example.com/jobs/5",
        required_skills=(),
        location="Remote",
        employment_type="Full-time",
    )

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=[],
            candidate_skills=[],
        ),
    )

    result = await use_case.execute(
        candidate_id=candidate_id,
        job_id=job_id,
    )

    assert result.score == 1.0
    assert result.decision == EvaluationDecision.STRONG_MATCH
    assert result.matched_skills == ()
    assert result.missing_skills == ()


@pytest.mark.asyncio
async def test_evaluate_job_returns_no_match_when_no_skills_match() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    javascript_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    job = Job(
        id=job_id,
        company="Acme",
        title="JavaScript Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/3",
        required_skills=(
            "JavaScript",
            "React",
        ),
        location="Remote",
        employment_type="Full-time",
    )

    skills = [
        Skill(id=javascript_id, name="JavaScript"),
    ]

    candidate_skills = []

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=skills,
            candidate_skills=candidate_skills,
        ),
    )

    result = await use_case.execute(
        candidate_id=candidate_id,
        job_id=job_id,
    )

    assert result.score == 0.0
    assert result.decision == EvaluationDecision.NO_MATCH

    assert result.matched_skills == ()
    assert result.missing_skills == (
        "JavaScript",
        "React",
    )


@pytest.mark.asyncio
async def test_evaluate_job_raises_when_job_does_not_exist() -> None:
    candidate_id = uuid4()
    job_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Abhindev Vijayan",
        email="abhindev@example.com",
        location="Kerala",
    )

    missing_job_id = job_id

    class MissingJobRepository:
        async def get_by_id(self, requested_job_id):
            assert requested_job_id == missing_job_id
            return None

    use_case = EvaluateJob(
        job_repository=MissingJobRepository(),
        candidate_repository=FakeCandidateRepository(candidate),
        skill_repository=FakeSkillRepository(
            skills=[],
            candidate_skills=[],
        ),
    )

    with pytest.raises(Exception, match=f"Job '{job_id}' was not found."):
        await use_case.execute(
            candidate_id=candidate_id,
            job_id=job_id,
        )


@pytest.mark.asyncio
async def test_evaluate_job_raises_when_candidate_does_not_exist() -> None:
    candidate_id = uuid4()
    job_id = uuid4()

    job = Job(
        id=job_id,
        company="Acme",
        title="Python Backend Developer",
        source="greenhouse",
        source_url="https://example.com/jobs/candidate-missing",
        required_skills=("Python",),
        location="Remote",
        employment_type="Full-time",
    )

    class MissingCandidateRepository:
        async def get_by_id(self, requested_candidate_id):
            assert requested_candidate_id == candidate_id
            return None

    use_case = EvaluateJob(
        job_repository=FakeJobRepository(job),
        candidate_repository=MissingCandidateRepository(),
        skill_repository=FakeSkillRepository(
            skills=[],
            candidate_skills=[],
        ),
    )

    with pytest.raises(
        CandidateNotFoundError,
        match=f"Candidate '{candidate_id}' was not found.",
    ):
        await use_case.execute(
            candidate_id=candidate_id,
            job_id=job_id,
        )
