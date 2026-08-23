from uuid import UUID

from packages.domain.applications.repositories import ApplicationRepository


class ApplicationNotFoundError(Exception):
    """Raised when the requested application does not exist."""


class DeleteApplication:
    """Use case for deleting an application."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        application_id: UUID,
    ) -> None:
        """Delete an existing application."""

        application = await self._repository.get_by_id(application_id)

        if application is None:
            raise ApplicationNotFoundError(
                f"Application '{application_id}' was not found.",
            )

        await self._repository.delete(application_id)
