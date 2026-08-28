from uuid import uuid4

import pytest

from packages.domain.agents.entities import AgentRun, AgentRunStatus


def test_agent_run_starts_as_pending() -> None:
    candidate_id = uuid4()

    agent_run = AgentRun(candidate_id=candidate_id)

    assert agent_run.candidate_id == candidate_id
    assert agent_run.status is AgentRunStatus.PENDING
    assert agent_run.started_at is None
    assert agent_run.completed_at is None


def test_agent_run_can_start() -> None:
    agent_run = AgentRun(candidate_id=uuid4())

    agent_run.start()

    assert agent_run.status is AgentRunStatus.RUNNING
    assert agent_run.started_at is not None


def test_agent_run_can_complete() -> None:
    agent_run = AgentRun(candidate_id=uuid4())

    agent_run.start()
    agent_run.complete()

    assert agent_run.status is AgentRunStatus.COMPLETED
    assert agent_run.completed_at is not None


def test_agent_run_can_fail() -> None:
    agent_run = AgentRun(candidate_id=uuid4())

    agent_run.start()
    agent_run.fail("Discovery service failed")

    assert agent_run.status is AgentRunStatus.FAILED
    assert agent_run.error_message == "Discovery service failed"
    assert agent_run.completed_at is not None


def test_pending_agent_run_cannot_complete() -> None:
    agent_run = AgentRun(candidate_id=uuid4())

    with pytest.raises(ValueError):
        agent_run.complete()


def test_completed_agent_run_cannot_start_again() -> None:
    agent_run = AgentRun(candidate_id=uuid4())

    agent_run.start()
    agent_run.complete()

    with pytest.raises(ValueError):
        agent_run.start()
