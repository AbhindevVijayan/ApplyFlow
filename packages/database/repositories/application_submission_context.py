from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.application import Application
from packages.database.models.candidate import Candidate
from packages.database.models.job import Job
from packages.database.models.resume import Resume
from packages.domain.applications.submission_context import (
    ApplicationSubmissionContext,
)
from packages.domain.applications.submission_repositories import (
    ApplicationSubmissionContextRepository,
)


class DatabaseApplicationSubmissionContextRepository(
    ApplicationSubmissionContextRepository,
):
    """Load complete application data required for external submission."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_application_id(
        self,
        application_id: UUID,
    ) -> ApplicationSubmissionContext | None:
        """Return submission context for an application."""

        statement = (
            select(
                Application.id,
                Candidate.id,
                Candidate.full_name,
                Candidate.email,
                Candidate.phone,
                Job.id,
                Job.title,
                Job.company,
                Job.source,
                Job.source_url,
                Resume.id,
                Resume.filename,
                Resume.storage_key,
            )
            .join(
                Candidate,
                Candidate.id == Application.candidate_id,
            )
            .join(
                Job,
                Job.id == Application.job_id,
            )
            .join(
                Resume,
                Resume.id == Application.resume_id,
            )
            .where(Application.id == application_id)
        )

        result = await self._session.execute(statement)
        row = result.one_or_none()

        if row is None:
            return None

        (
            application_id,
            candidate_id,
            candidate_name,
            candidate_email,
            candidate_phone,
            job_id,
            job_title,
            company,
            source,
            source_url,
            resume_id,
            resume_filename,
            resume_storage_key,
        ) = row

        return ApplicationSubmissionContext(
            application_id=application_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            job_id=job_id,
            job_title=job_title,
            company=company,
            source=source,
            source_url=source_url,
            resume_id=resume_id,
            resume_filename=resume_filename,
            resume_storage_key=resume_storage_key,
        )
