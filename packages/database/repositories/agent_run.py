from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.agent_run import AgentRun


class AgentRunRepository:
    """Persistence operations for AgentRun entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, agent_run: AgentRun) -> AgentRun:
        """Persist a new agent run."""
        self._session.add(agent_run)
        await self._session.flush()
        await self._session.refresh(agent_run)

        return agent_run

    async def get_by_id(
        self,
        agent_run_id: UUID,
    ) -> AgentRun | None:
        """Return an agent run by ID."""
        statement = select(AgentRun).where(
            AgentRun.id == agent_run_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_candidate(
        self,
        candidate_id: UUID,
    ) -> Sequence[AgentRun]:
        """Return agent runs for a candidate."""
        statement = (
            select(AgentRun)
            .where(AgentRun.candidate_id == candidate_id)
            .order_by(
                AgentRun.created_at.asc(),
                AgentRun.id.asc(),
            )
        )

        result = await self._session.execute(statement)

        return result.scalars().all()

    async def update(self, agent_run: AgentRun) -> AgentRun:
        """Persist changes to an existing agent run."""
        await self._session.flush()
        await self._session.refresh(agent_run)

        return agent_run
