from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base

if TYPE_CHECKING:
    from packages.database.models.candidate import Candidate
    from packages.database.models.job_skill import JobSkill


class Skill(Base):
    """Persistence model for a skill."""

    __tablename__ = "skills"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    candidates: Mapped[list["CandidateSkill"]] = relationship(
        back_populates="skill",
        passive_deletes=True,
    )

    job_links: Mapped[list["JobSkill"]] = relationship(
        back_populates="skill",
        passive_deletes=True,
    )


class CandidateSkill(Base):
    """Association between a candidate and a skill."""

    __tablename__ = "candidate_skills"

    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    skill_id: Mapped[UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )

    proficiency: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="skills",
    )

    skill: Mapped["Skill"] = relationship(
        back_populates="candidates",
    )

    __table_args__ = (
        Index(
            "ix_candidate_skills_skill_id",
            "skill_id",
        ),
    )
