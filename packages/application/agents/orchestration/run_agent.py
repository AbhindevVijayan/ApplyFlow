from uuid import UUID

from packages.domain.agents.entities import AgentRun
from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)


class RunAgent:
    """Application service for starting an agent run."""

    def __init__(self, repository: AgentRunRepository) -> None:
        self._repository = repository

    async def execute(self, candidate_id: UUID) -> AgentRun:
        """Create and persist a new agent run."""
        agent_run = AgentRun(candidate_id=candidate_id)

        return await self._repository.create(agent_run)
