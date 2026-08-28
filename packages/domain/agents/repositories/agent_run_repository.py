from abc import ABC, abstractmethod
from uuid import UUID

from packages.domain.agents.entities import AgentRun


class AgentRunRepository(ABC):
    @abstractmethod
    async def create(self, agent_run: AgentRun) -> AgentRun:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self,
        agent_run_id: UUID,
    ) -> AgentRun | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, agent_run: AgentRun) -> AgentRun:
        raise NotImplementedError
