from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Skill:
    """Domain representation of a candidate skill."""

    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class CandidateSkill:
    """Domain representation of a skill assigned to a candidate."""

    candidate_id: UUID
    skill_id: UUID
    proficiency: str | None = None
