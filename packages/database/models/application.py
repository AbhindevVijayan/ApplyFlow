from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base

if TYPE_CHECKING:
    from packages.database.models.candidate import Candidate
    from packages.database.models.job import Job
    from packages.database.models.resume import Resume


class Application(Base):
    """Persistence model for a job application."""

    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "job_id",
            name="uq_applications_candidate_job",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    external_application_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    candidate: Mapped["Candidate"] = relationship()

    job: Mapped["Job"] = relationship()

    resume: Mapped["Resume"] = relationship()
