from uuid import UUID

from packages.domain.resumes.repository import ResumeRepository


class DeleteResume:
    """Use case for deleting a resume."""

    def __init__(self, repository: ResumeRepository) -> None:
        self._repository = repository

    async def execute(self, resume_id: UUID) -> None:
        """Delete a resume by ID if it exists."""
        resume = await self._repository.get_by_id(resume_id)

        if resume is None:
            return

        await self._repository.delete(resume_id)
