from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CandidateExperience:
    """Professional experience associated with a candidate."""

    id: UUID
    candidate_id: UUID

    company_name: str
    job_title: str

    employment_type: str | None = None
    location: str | None = None

    start_date: date | None = None
    end_date: date | None = None

    description: str | None = None

    is_current: bool = False
