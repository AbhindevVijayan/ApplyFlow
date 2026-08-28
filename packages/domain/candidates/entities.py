from dataclasses import dataclass
from uuid import UUID

from packages.domain.candidates.profile import CandidateProfile


@dataclass(frozen=True, slots=True)
class Candidate:
    """Domain representation of a candidate."""

    id: UUID
    full_name: str
    email: str

    phone: str | None = None
    location: str | None = None

    profile: CandidateProfile | None = None
