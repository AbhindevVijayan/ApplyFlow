from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from packages.application.agents.orchestration.orchestrate_agent import (
    AgentOrchestrator,
)
from packages.domain.agents.entities import AgentRun
from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)
from packages.domain.applications.entities import Application
from packages.domain.applications.gateway import ApplicationSubmissionGateway
from packages.domain.applications.repositories import ApplicationRepository
from packages.domain.applications.submission import (
    SubmissionResult,
    SubmissionStatus,
)
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)
from packages.domain.applications.submission_repositories import (
    ApplicationSubmissionContextRepository,
)
from packages.domain.candidates.entities import Candidate
from packages.domain.candidates.repository import CandidateRepository
from packages.domain.discovery.entities import DiscoveredJob
from packages.domain.discovery.sources import JobSource
from packages.domain.jobs.entities import Job
from packages.domain.resumes.entities import Resume
from packages.domain.resumes.repository import ResumeRepository
from packages.domain.skills.repository import SkillRepository
from packages.infrastructure.requirements.keyword_extractor import (
    KeywordJobRequirementsExtractor,
)


class FakeAgentRunRepository(AgentRunRepository):
    def __init__(self) -> None:
        self.agent_runs: dict[UUID, AgentRun] = {}

    async def create(self, agent_run: AgentRun) -> AgentRun:
        self.agent_runs[agent_run.id] = agent_run
        return agent_run

    async def get_by_id(
        self,
        agent_run_id: UUID,
    ) -> AgentRun | None:
        return self.agent_runs.get(agent_run_id)

    async def update(self, agent_run: AgentRun) -> AgentRun:
        self.agent_runs[agent_run.id] = agent_run
        return agent_run


class FakeJobRepository:
    def __init__(self) -> None:
        self.jobs: dict[UUID, Job] = {}
        self.jobs_by_source_url: dict[str, Job] = {}

    async def create(self, job: Job) -> Job:
        self.jobs[job.id] = job
        self.jobs_by_source_url[job.source_url] = job
        return job

    async def get_by_id(
        self,
        job_id: UUID,
    ) -> Job | None:
        return self.jobs.get(job_id)

    async def get_by_source_url(
        self,
        source_url: str,
    ) -> Job | None:
        return self.jobs_by_source_url.get(source_url)

    async def list_all(self) -> list[Job]:
        return list(self.jobs.values())

    async def update(self, job: Job) -> Job:
        self.jobs[job.id] = job
        self.jobs_by_source_url[job.source_url] = job
        return job

    async def delete(self, job_id: UUID) -> None:
        job = self.jobs.pop(job_id, None)

        if job is not None:
            self.jobs_by_source_url.pop(
                job.source_url,
                None,
            )


class FakeCandidateRepository(CandidateRepository):
    def __init__(self, candidate: Candidate) -> None:
        self._candidate = candidate

    async def create(self, candidate: Candidate) -> Candidate:
        self._candidate = candidate
        return candidate

    async def get_by_id(
        self,
        candidate_id: UUID,
    ) -> Candidate | None:
        if candidate_id == self._candidate.id:
            return self._candidate

        return None

    async def get_by_email(
        self,
        email: str,
    ) -> Candidate | None:
        if email == self._candidate.email:
            return self._candidate

        return None

    async def update(self, candidate: Candidate) -> Candidate:
        self._candidate = candidate
        return candidate

    async def delete(self, candidate_id: UUID) -> None:
        return None

    async def list_all(self) -> list[Candidate]:
        return [self._candidate]


class FakeSkillRepository(SkillRepository):
    async def get_candidate_skills(
        self,
        candidate_id: UUID,
    ) -> list:
        return []

    async def get_by_id(self, skill_id: UUID):
        return None


class FakeResumeRepository(ResumeRepository):
    def __init__(self, resume: Resume) -> None:
        self._resume = resume

    async def create(self, resume: Resume) -> Resume:
        self._resume = resume
        return resume

    async def get_by_id(
        self,
        resume_id: UUID,
    ) -> Resume | None:
        if resume_id == self._resume.id:
            return self._resume

        return None

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Resume]:
        if candidate_id == self._resume.candidate_id:
            return [self._resume]

        return []

    async def get_canonical_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Resume | None:
        if candidate_id == self._resume.candidate_id and self._resume.is_canonical:
            return self._resume

        return None

    async def update(self, resume: Resume) -> Resume:
        self._resume = resume
        return resume

    async def delete(self, resume_id: UUID) -> None:
        return None


class FakeApplicationRepository(ApplicationRepository):
    def __init__(self) -> None:
        self.applications: list[Application] = []

    async def create(
        self,
        application: Application,
    ) -> Application:
        self.applications.append(application)
        return application

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> Application | None:
        return next(
            (application for application in self.applications if application.id == application_id),
            None,
        )

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Application]:
        return [
            application
            for application in self.applications
            if application.candidate_id == candidate_id
        ]

    async def get_by_job_id(
        self,
        job_id: UUID,
    ) -> list[Application]:
        return [application for application in self.applications if application.job_id == job_id]

    async def get_by_candidate_and_job(
        self,
        candidate_id: UUID,
        job_id: UUID,
    ) -> Application | None:
        return next(
            (
                application
                for application in self.applications
                if (application.candidate_id == candidate_id and application.job_id == job_id)
            ),
            None,
        )

    async def update(
        self,
        application: Application,
    ) -> Application:
        for index, existing in enumerate(self.applications):
            if existing.id == application.id:
                self.applications[index] = application
                return application

        return application

    async def delete(
        self,
        application_id: UUID,
    ) -> None:
        self.applications = [
            application for application in self.applications if application.id != application_id
        ]


class FakeSubmissionContextRepository(
    ApplicationSubmissionContextRepository,
):
    def __init__(
        self,
        candidate_id: UUID,
        resume_id: UUID,
    ) -> None:
        self._candidate_id = candidate_id
        self._resume_id = resume_id

    async def get_by_application_id(
        self,
        application_id: UUID,
    ) -> ApplicationSubmissionContext | None:
        return ApplicationSubmissionContext(
            application_id=application_id,
            candidate_id=self._candidate_id,
            candidate_name="Test Candidate",
            candidate_email="candidate@example.com",
            candidate_phone=None,
            job_id=uuid4(),
            job_title="Python Developer",
            company="Example Company",
            source="fake",
            source_url="https://example.com/jobs/python",
            resume_id=self._resume_id,
            resume_filename="resume.pdf",
            resume_storage_key="resumes/test.pdf",
        )


class FakeSubmissionGateway(ApplicationSubmissionGateway):
    async def submit(
        self,
        context: ApplicationSubmissionContext,
    ) -> SubmissionResult:
        return SubmissionResult(
            status=SubmissionStatus.SUBMITTED,
            external_application_url=("https://example.com/applications/submitted"),
        )


class FakeJobSource(JobSource):
    @property
    def name(self) -> str:
        return "fake"

    async def discover(self) -> list[DiscoveredJob]:
        return [
            DiscoveredJob(
                company="Example Company",
                title="Python Developer",
                source="fake",
                source_url="https://example.com/jobs/python",
                description="Python developer position.",
                location="Remote",
                employment_type="full-time",
                discovered_at=datetime.now(UTC),
            ),
        ]


@pytest.mark.asyncio
async def test_agent_orchestrator_runs_full_workflow() -> None:
    candidate_id = uuid4()
    resume_id = uuid4()

    candidate = Candidate(
        id=candidate_id,
        full_name="Test Candidate",
        email="candidate@example.com",
        location="Remote",
    )

    resume = Resume(
        id=resume_id,
        candidate_id=candidate_id,
        filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resumes/test.pdf",
        is_canonical=True,
    )

    agent_run_repository = FakeAgentRunRepository()
    job_repository = FakeJobRepository()
    candidate_repository = FakeCandidateRepository(candidate)
    resume_repository = FakeResumeRepository(resume)
    application_repository = FakeApplicationRepository()
    skill_repository = FakeSkillRepository()
    submission_context_repository = FakeSubmissionContextRepository(
        candidate_id=candidate_id,
        resume_id=resume_id,
    )

    submission_gateway = FakeSubmissionGateway()

    orchestrator = AgentOrchestrator(
        sources=[FakeJobSource()],
        agent_run_repository=agent_run_repository,
        job_repository=job_repository,
        candidate_repository=candidate_repository,
        skill_repository=skill_repository,
        resume_repository=resume_repository,
        application_repository=application_repository,
        submission_context_repository=submission_context_repository,
        submission_gateway=submission_gateway,
        requirements_extractor=KeywordJobRequirementsExtractor(),
    )

    result = await orchestrator.execute(candidate_id)

    assert result.status.value == "completed"
    assert result.jobs_discovered == 1
    assert result.jobs_evaluated == 1
