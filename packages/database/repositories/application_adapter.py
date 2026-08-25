from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.mappers.application import to_domain, to_model
from packages.database.repositories.application import (
    ApplicationRepository as DatabaseApplicationRepository,
)
from packages.domain.applications.entities import Application
from packages.domain.applications.repositories import ApplicationRepository


class ApplicationRepositoryAdapter(ApplicationRepository):
    """Adapt the SQLAlchemy application repository to the domain port."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = DatabaseApplicationRepository(session)

    async def create(
        self,
        application: Application,
    ) -> Application:
        """Persist a domain application."""

        model = to_model(application)
        created = await self._repository.create(model)

        return to_domain(created)

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> Application | None:
        """Find an application by ID."""

        model = await self._repository.get_by_id(application_id)

        if model is None:
            return None

        return to_domain(model)

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> Sequence[Application]:
        """Return applications belonging to a candidate."""

        models = await self._repository.get_by_candidate_id(
            candidate_id,
        )

        return [to_domain(model) for model in models]

    async def get_by_job_id(
        self,
        job_id: UUID,
    ) -> Sequence[Application]:
        """Return applications for a job."""

        models = await self._repository.get_by_job_id(job_id)

        return [to_domain(model) for model in models]

    async def get_by_candidate_and_job(
        self,
        candidate_id: UUID,
        job_id: UUID,
    ) -> Application | None:
        """Return an application for a candidate/job pair."""

        model = await self._repository.get_by_candidate_and_job(
            candidate_id,
            job_id,
        )

        if model is None:
            return None

        return to_domain(model)

    async def update(
        self,
        application: Application,
    ) -> Application:
        """Persist changes to a domain application."""

        model = await self._repository.get_by_id(application.id)

        if model is None:
            raise ValueError(
                f"Application '{application.id}' does not exist.",
            )

        model.candidate_id = application.candidate_id
        model.job_id = application.job_id
        model.resume_id = application.resume_id
        model.status = application.status.value
        model.applied_at = application.applied_at
        model.external_application_url = application.external_application_url
        model.notes = application.notes
        model.failure_reason = application.failure_reason

        updated = await self._repository.update(model)

        return to_domain(updated)

    async def delete(
        self,
        application_id: UUID,
    ) -> None:
        """Delete an application by ID."""

        model = await self._repository.get_by_id(application_id)

        if model is None:
            return

        await self._repository.delete(model)
