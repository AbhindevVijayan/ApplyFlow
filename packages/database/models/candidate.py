from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.database.base import Base
from packages.database.models.candidate_profile import CandidateProfile
from packages.database.models.skill import CandidateSkill

if TYPE_CHECKING:
    from packages.database.models.resume import Resume


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
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

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    skills: Mapped[list["CandidateSkill"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    profile: Mapped["CandidateProfile | None"] = relationship(
        back_populates="candidate",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
