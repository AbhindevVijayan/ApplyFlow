from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class JobSkill:
    """Required skill associated with a job."""

    job_id: UUID
    skill_id: UUID
