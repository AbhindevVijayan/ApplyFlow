from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from packages.domain.skills.entities import CandidateSkill, Skill


class SkillRepository(Protocol):
    """Persistence contract for skills and candidate-skill associations."""

    async def create(self, skill: Skill) -> Skill:
        """Persist a new skill."""
        ...

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        """Return a skill by ID."""
        ...

    async def get_by_name(self, name: str) -> Skill | None:
        """Return a skill by name."""
        ...

    async def list_all(self) -> Sequence[Skill]:
        """Return all skills."""
        ...

    async def update(self, skill: Skill) -> Skill:
        """Update an existing skill."""
        ...

    async def delete(self, skill_id: UUID) -> None:
        """Delete a skill by ID."""
        ...

    async def add_to_candidate(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Associate a skill with a candidate."""
        ...

    async def get_candidate_skill(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> CandidateSkill | None:
        """Return a candidate-skill association."""
        ...

    async def get_candidate_skills(
        self,
        candidate_id: UUID,
    ) -> Sequence[CandidateSkill]:
        """Return all skills associated with a candidate."""
        ...

    async def update_candidate_skill(
        self,
        candidate_skill: CandidateSkill,
    ) -> CandidateSkill:
        """Update a candidate-skill association."""
        ...

    async def remove_from_candidate(
        self,
        candidate_id: UUID,
        skill_id: UUID,
    ) -> None:
        """Remove a skill association from a candidate."""
        ...
