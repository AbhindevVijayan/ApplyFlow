from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class AgentRun(Base):
    """Persistence model for an agent execution."""

    __tablename__ = "agent_runs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    jobs_discovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_evaluated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    applications_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
