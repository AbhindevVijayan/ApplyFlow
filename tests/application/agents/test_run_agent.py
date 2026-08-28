from uuid import UUID, uuid4

from packages.application.agents.orchestration.run_agent import RunAgent
from packages.domain.agents.entities import AgentRun, AgentRunStatus
from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)


class FakeAgentRunRepository(AgentRunRepository):
    def __init__(self) -> None:
        self.created_agent_run: AgentRun | None = None

    async def create(self, agent_run: AgentRun) -> AgentRun:
        self.created_agent_run = agent_run
        return agent_run

    async def get_by_id(self, agent_run_id: UUID) -> AgentRun | None:
        return None

    async def update(self, agent_run: AgentRun) -> AgentRun:
        return agent_run


async def test_run_agent_creates_and_persists_pending_agent_run() -> None:
    candidate_id = uuid4()
    repository = FakeAgentRunRepository()

    use_case = RunAgent(repository)

    result = await use_case.execute(candidate_id)

    assert result.candidate_id == candidate_id
    assert result.status == AgentRunStatus.PENDING
    assert repository.created_agent_run == result
