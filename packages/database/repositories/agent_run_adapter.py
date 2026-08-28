from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.agent_run import to_domain, to_model
from packages.database.repositories.agent_run import (
    AgentRunRepository as DatabaseAgentRunRepository,
)
from packages.domain.agents.entities import AgentRun
from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)


class AgentRunRepositoryAdapter(AgentRunRepository):
    """Adapt the SQLAlchemy agent-run repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseAgentRunRepository(session)

    async def create(self, agent_run: AgentRun) -> AgentRun:
        """Persist a domain agent run."""
        model = to_model(agent_run)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(
        self,
        agent_run_id: UUID,
    ) -> AgentRun | None:
        """Find an agent run by ID."""
        model = await self._repository.get_by_id(agent_run_id)

        if model is None:
            return None

        return to_domain(model)

    async def update(self, agent_run: AgentRun) -> AgentRun:
        """Update and persist a domain agent run."""
        model = await self._repository.get_by_id(agent_run.id)

        if model is None:
            raise ValueError(
                f"Agent run '{agent_run.id}' does not exist.",
            )

        model.candidate_id = agent_run.candidate_id
        model.status = agent_run.status.value
        model.started_at = agent_run.started_at
        model.completed_at = agent_run.completed_at
        model.jobs_discovered = agent_run.jobs_discovered
        model.jobs_evaluated = agent_run.jobs_evaluated
        model.applications_created = agent_run.applications_created
        model.error_message = agent_run.error_message

        updated = await self._repository.update(model)

        return to_domain(updated)
