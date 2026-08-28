from packages.database.models.agent_run import AgentRun as AgentRunModel
from packages.domain.agents.entities import AgentRun as AgentRunDomain
from packages.domain.agents.entities import AgentRunStatus


def to_domain(model: AgentRunModel) -> AgentRunDomain:
    """Convert a database agent run into a domain agent run."""
    return AgentRunDomain(
        id=model.id,
        candidate_id=model.candidate_id,
        status=AgentRunStatus(model.status),
        started_at=model.started_at,
        completed_at=model.completed_at,
        jobs_discovered=model.jobs_discovered,
        jobs_evaluated=model.jobs_evaluated,
        applications_created=model.applications_created,
        error_message=model.error_message,
        created_at=model.created_at,
    )


def to_model(agent_run: AgentRunDomain) -> AgentRunModel:
    """Convert a domain agent run into a database agent run."""
    return AgentRunModel(
        id=agent_run.id,
        candidate_id=agent_run.candidate_id,
        status=agent_run.status.value,
        started_at=agent_run.started_at,
        completed_at=agent_run.completed_at,
        jobs_discovered=agent_run.jobs_discovered,
        jobs_evaluated=agent_run.jobs_evaluated,
        applications_created=agent_run.applications_created,
        error_message=agent_run.error_message,
    )
