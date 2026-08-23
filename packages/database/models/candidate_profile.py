from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base

if TYPE_CHECKING:
    from packages.database.models.candidate import Candidate


class CandidateProfile(Base):
    """Professional profile associated with a candidate."""

    __tablename__ = "candidate_profiles"

    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    headline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    years_of_experience: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    current_job_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    current_company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    current_salary: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    expected_salary: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    notice_period_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    highest_qualification: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    career_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    work_authorization: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    willing_to_relocate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    remote_preference: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="profile",
    )