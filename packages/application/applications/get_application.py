from uuid import UUID

from packages.domain.applications.entities import Application
from packages.domain.applications.repositories import ApplicationRepository


class ApplicationNotFoundError(Exception):
    """Raised when the requested application does not exist."""


class GetApplication:
    """Use case for retrieving an application."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        application_id: UUID,
    ) -> Application:
        """Retrieve an application by ID."""

        application = await self._repository.get_by_id(application_id)

        if application is None:
            raise ApplicationNotFoundError(
                f"Application '{application_id}' was not found.",
            )

        return application
