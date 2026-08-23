from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class CandidateEducation(Base):
    """Persistence model for candidate education."""

    __tablename__ = "candidate_education"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "candidates.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    institution: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    degree: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    field_of_study: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    grade: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )