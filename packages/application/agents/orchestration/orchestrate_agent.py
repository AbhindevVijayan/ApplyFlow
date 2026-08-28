from collections.abc import Sequence
from uuid import UUID

from packages.application.agents.orchestration.run_agent import RunAgent
from packages.application.applications.create_application import (
    ApplicationAlreadyExistsError,
    CreateApplication,
    CreateApplicationCommand,
)
from packages.application.discovery.run_discovery import RunDiscovery
from packages.application.evaluation.evaluate_job import EvaluateJob
from packages.domain.agents.entities import AgentRun
from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)
from packages.domain.applications.repositories import ApplicationRepository
from packages.domain.candidates.repository import CandidateRepository
from packages.domain.discovery.sources import JobSource
from packages.domain.evaluation.enums import EvaluationDecision
from packages.domain.jobs.repositories import JobRepository
from packages.domain.requirements.extractor import JobRequirementsExtractor
from packages.domain.resumes.repository import ResumeRepository
from packages.domain.skills.repository import SkillRepository


class AgentOrchestrator:
    """Coordinate the complete job discovery and application workflow."""

    def __init__(
        self,
        *,
        sources: Sequence[JobSource],
        agent_run_repository: AgentRunRepository,
        job_repository: JobRepository,
        candidate_repository: CandidateRepository,
        skill_repository: SkillRepository,
        resume_repository: ResumeRepository,
        application_repository: ApplicationRepository,
        requirements_extractor: JobRequirementsExtractor,
    ) -> None:
        self._sources = sources
        self._agent_run_repository = agent_run_repository
        self._job_repository = job_repository
        self._candidate_repository = candidate_repository
        self._skill_repository = skill_repository
        self._resume_repository = resume_repository
        self._application_repository = application_repository
        self._requirements_extractor = requirements_extractor

    async def execute(
        self,
        candidate_id: UUID,
    ) -> AgentRun:
        """Run discovery, evaluation, and application creation."""

        run_agent = RunAgent(
            self._agent_run_repository,
        )

        agent_run = await run_agent.execute(candidate_id)

        try:
            agent_run.start()

            agent_run = await self._agent_run_repository.update(
                agent_run,
            )

            discovery = RunDiscovery(
                sources=self._sources,
                repository=self._job_repository,
                requirements_extractor=self._requirements_extractor,
            )

            discovery_results = await discovery.execute()

            agent_run.jobs_discovered = sum(result.persisted_count for result in discovery_results)

            agent_run = await self._agent_run_repository.update(
                agent_run,
            )

            canonical_resume = await self._resume_repository.get_canonical_by_candidate_id(
                candidate_id
            )

            if canonical_resume is None:
                raise ValueError(
                    "Candidate does not have a canonical resume.",
                )

            evaluate_job = EvaluateJob(
                job_repository=self._job_repository,
                candidate_repository=self._candidate_repository,
                skill_repository=self._skill_repository,
            )

            create_application = CreateApplication(
                self._application_repository,
            )

            for discovery_result in discovery_results:
                if discovery_result.status != "completed":
                    continue

                for job in discovery_result.jobs:
                    evaluation = await evaluate_job.execute(
                        candidate_id=candidate_id,
                        job_id=job.id,
                    )

                    agent_run.jobs_evaluated += 1

                    if evaluation.decision not in (
                        EvaluationDecision.STRONG_MATCH,
                        EvaluationDecision.MATCH,
                    ):
                        continue

                    try:
                        await create_application.execute(
                            CreateApplicationCommand(
                                candidate_id=candidate_id,
                                job_id=job.id,
                                resume_id=canonical_resume.id,
                            ),
                        )

                        agent_run.applications_created += 1

                    except ApplicationAlreadyExistsError:
                        continue

            agent_run.complete()

            return await self._agent_run_repository.update(
                agent_run,
            )

        except Exception as exc:
            agent_run.fail(str(exc))

            await self._agent_run_repository.update(agent_run)

            raise
