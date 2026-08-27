from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base

if TYPE_CHECKING:
    from packages.database.models.job import Job
    from packages.database.models.skill import Skill


class JobSkill(Base):
    """Association between a job and one of its required skills."""

    __tablename__ = "job_required_skills"

    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
    )

    skill_id: Mapped[UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )

    job: Mapped["Job"] = relationship(
        back_populates="required_skill_links",
    )

    skill: Mapped["Skill"] = relationship(
        back_populates="job_links",
    )

    __table_args__ = (
        Index(
            "ix_job_required_skills_skill_id",
            "skill_id",
        ),
    )