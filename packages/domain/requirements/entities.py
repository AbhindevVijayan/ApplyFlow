from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JobRequirements:
    """Requirements extracted from a job posting."""

    required_skills: tuple[str, ...]
