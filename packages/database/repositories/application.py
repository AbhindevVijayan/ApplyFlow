from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.application import Application


class ApplicationRepository:
    """Persistence operations for Application entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        application: Application,
    ) -> Application:
        """Persist a new application."""

        self._session.add(application)

        await self._session.flush()
        await self._session.refresh(application)

        return application

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> Application | None:
        """Return an application by ID."""

        statement = select(Application).where(
            Application.id == application_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self,
        candidate_id: UUID,
    ) -> list[Application]:
        """Return applications belonging to a candidate."""

        statement = (
            select(Application)
            .where(Application.candidate_id == candidate_id)
            .order_by(Application.created_at.desc())
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_by_job_id(
        self,
        job_id: UUID,
    ) -> list[Application]:
        """Return applications for a job."""

        statement = (
            select(Application)
            .where(Application.job_id == job_id)
            .order_by(Application.created_at.desc())
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_by_candidate_and_job(
        self,
        candidate_id: UUID,
        job_id: UUID,
    ) -> Application | None:
        """Return an application for a candidate/job pair."""

        statement = select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_id == job_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def update(
        self,
        application: Application,
    ) -> Application:
        """Persist changes to an existing application."""

        existing = await self.get_by_id(application.id)

        if existing is None:
            raise ValueError(
                f"Application not found: {application.id}",
            )

        existing.candidate_id = application.candidate_id
        existing.job_id = application.job_id
        existing.resume_id = application.resume_id
        existing.status = application.status
        existing.applied_at = application.applied_at
        existing.external_application_url = application.external_application_url
        existing.notes = application.notes
        existing.failure_reason = application.failure_reason

        await self._session.flush()
        await self._session.refresh(existing)

        return existing

    async def delete(
        self,
        application_id: UUID,
    ) -> None:
        """Delete an application."""

        application = await self.get_by_id(application_id)

        if application is None:
            raise ValueError(
                f"Application not found: {application_id}",
            )

        await self._session.delete(application)
        await self._session.flush()
