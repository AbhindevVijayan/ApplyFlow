from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base

if TYPE_CHECKING:
    from packages.database.models.job_skill import JobSkill


class Job(Base):
    """Persistence model for a job posting."""

    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    company: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        String(768),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    discovered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    required_skill_links: Mapped[list["JobSkill"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )