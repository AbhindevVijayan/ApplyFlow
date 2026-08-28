from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class AgentRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentRun:
    candidate_id: UUID

    id: UUID = field(default_factory=uuid4)

    status: AgentRunStatus = AgentRunStatus.PENDING

    started_at: datetime | None = None
    completed_at: datetime | None = None

    jobs_discovered: int = 0
    jobs_evaluated: int = 0
    applications_created: int = 0

    error_message: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def start(self) -> None:
        if self.status is not AgentRunStatus.PENDING:
            raise ValueError(f"Cannot start agent run with status '{self.status}'")

        self.status = AgentRunStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        if self.status is not AgentRunStatus.RUNNING:
            raise ValueError(f"Cannot complete agent run with status '{self.status}'")

        self.status = AgentRunStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

    def fail(self, error_message: str) -> None:
        if self.status not in (
            AgentRunStatus.PENDING,
            AgentRunStatus.RUNNING,
        ):
            raise ValueError(f"Cannot fail agent run with status '{self.status}'")

        self.status = AgentRunStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.error_message = error_message
