from dataclasses import dataclass
from uuid import UUID

from packages.domain.resumes.entities import Resume
from packages.domain.resumes.repository import ResumeRepository


@dataclass(frozen=True, slots=True)
class UpdateResumeCommand:
    """Data required to update a resume."""

    resume_id: UUID
    filename: str
    content_type: str
    storage_key: str
    parsed_text: str | None = None
    is_canonical: bool = False


class UpdateResume:
    """Use case for updating a resume."""

    def __init__(self, repository: ResumeRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: UpdateResumeCommand,
    ) -> Resume:
        """Update and persist a resume."""

        existing = await self._repository.get_by_id(command.resume_id)

        if existing is None:
            raise ValueError(
                f"Resume {command.resume_id} not found.",
            )

        if command.is_canonical:
            existing_canonical = await self._repository.get_canonical_by_candidate_id(
                existing.candidate_id,
            )

            if existing_canonical is not None and existing_canonical.id != existing.id:
                demoted = Resume(
                    id=existing_canonical.id,
                    candidate_id=existing_canonical.candidate_id,
                    filename=existing_canonical.filename,
                    content_type=existing_canonical.content_type,
                    storage_key=existing_canonical.storage_key,
                    parsed_text=existing_canonical.parsed_text,
                    is_canonical=False,
                    created_at=existing_canonical.created_at,
                )

                await self._repository.update(demoted)

        updated = Resume(
            id=existing.id,
            candidate_id=existing.candidate_id,
            filename=command.filename,
            content_type=command.content_type,
            storage_key=command.storage_key,
            parsed_text=command.parsed_text,
            is_canonical=command.is_canonical,
            created_at=existing.created_at,
        )

        return await self._repository.update(updated)
