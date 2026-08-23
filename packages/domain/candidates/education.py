from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CandidateEducation:
    """Educational qualification associated with a candidate."""

    id: UUID
    candidate_id: UUID

    institution: str
    degree: str

    field_of_study: str | None = None

    start_date: date | None = None
    end_date: date | None = None

    grade: str | None = None

    is_current: bool = False