from abc import ABC

from packages.domain.agents.repositories.agent_run_repository import (
    AgentRunRepository,
)


def test_agent_run_repository_is_abstract() -> None:
    assert issubclass(AgentRunRepository, ABC)
