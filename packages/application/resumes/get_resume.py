from dataclasses import dataclass
from uuid import UUID

from packages.domain.resumes.entities import Resume
from packages.domain.resumes.repository import ResumeRepository


@dataclass(frozen=True, slots=True)
class GetResumeCommand:
    """Request for retrieving resumes."""

    resume_id: UUID | None = None
    candidate_id: UUID | None = None
    canonical_only: bool = False


class GetResume:
    """Use case for retrieving resumes."""

    def __init__(self, repository: ResumeRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: GetResumeCommand,
    ) -> Resume | list[Resume] | None:
        """Retrieve a resume or resumes according to the command."""

        if command.resume_id is not None:
            return await self._repository.get_by_id(command.resume_id)

        if command.candidate_id is None:
            raise ValueError(
                "candidate_id is required when resume_id is not provided.",
            )

        if command.canonical_only:
            return await self._repository.get_canonical_by_candidate_id(
                command.candidate_id,
            )

        return list(
            await self._repository.get_by_candidate_id(
                command.candidate_id,
            ),
        )
