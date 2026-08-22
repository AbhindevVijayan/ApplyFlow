from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.schemas import (
    CreateJobRequest,
    JobResponse,
    UpdateJobRequest,
)
from packages.application.jobs.create_job import (
    CreateJob,
    CreateJobCommand,
    JobAlreadyExistsError,
)
from packages.application.jobs.delete_job import (
    DeleteJob,
)
from packages.application.jobs.delete_job import (
    JobNotFoundError as DeleteJobNotFoundError,
)
from packages.application.jobs.get_job import (
    GetJob,
)
from packages.application.jobs.get_job import (
    JobNotFoundError as GetJobNotFoundError,
)
from packages.application.jobs.list_jobs import ListJobs
from packages.application.jobs.update_job import (
    UNSET,
    JobSourceURLAlreadyExistsError,
    Unset,
    UpdateJob,
    UpdateJobCommand,
)
from packages.application.jobs.update_job import (
    JobNotFoundError as UpdateJobNotFoundError,
)
from packages.database.repositories.job_adapter import (
    JobRepositoryAdapter,
)
from packages.database.session import get_session
from packages.domain.jobs.entities import Job

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


def get_job_repository(
    session: SessionDependency,
) -> JobRepositoryAdapter:
    """Build the job repository for the current request."""
    return JobRepositoryAdapter(session)


RepositoryDependency = Annotated[
    JobRepositoryAdapter,
    Depends(get_job_repository),
]


def to_response(job: Job) -> JobResponse:
    """Convert a domain job into an HTTP response."""
    return JobResponse(
        id=job.id,
        company=job.company,
        title=job.title,
        source=job.source,
        source_url=job.source_url,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        discovered_at=job.discovered_at,
        created_at=job.created_at,
    )


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    payload: CreateJobRequest,
    repository: RepositoryDependency,
) -> JobResponse:
    """Create a job posting."""

    use_case = CreateJob(repository)

    try:
        job = await use_case.execute(
            CreateJobCommand(
                company=payload.company,
                title=payload.title,
                source=payload.source,
                source_url=payload.source_url,
                description=payload.description,
                location=payload.location,
                employment_type=payload.employment_type,
                discovered_at=payload.discovered_at,
            ),
        )
    except JobAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_response(job)


@router.get(
    "",
    response_model=list[JobResponse],
    status_code=status.HTTP_200_OK,
)
async def list_jobs(
    repository: RepositoryDependency,
) -> list[JobResponse]:
    """Return all jobs."""

    use_case = ListJobs(repository)

    jobs = await use_case.execute()

    return [to_response(job) for job in jobs]


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
)
async def get_job(
    job_id: UUID,
    repository: RepositoryDependency,
) -> JobResponse:
    """Return a job by ID."""

    use_case = GetJob(repository)

    try:
        job = await use_case.execute(job_id)
    except GetJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return to_response(job)


def get_required_update_value(
    value: str | None,
    field_name: str,
    fields: set[str],
) -> str | Unset:
    """Return a required update value or UNSET."""

    if field_name not in fields:
        return UNSET

    if value is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} cannot be null.",
        )

    return value


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
)
async def update_job(
    job_id: UUID,
    payload: UpdateJobRequest,
    repository: RepositoryDependency,
) -> JobResponse:
    """Partially update a job."""

    fields = payload.model_fields_set

    use_case = UpdateJob(repository)

    try:
        job = await use_case.execute(
            UpdateJobCommand(
                job_id=job_id,
                company=get_required_update_value(
                    payload.company,
                    "company",
                    fields,
                ),
                title=get_required_update_value(
                    payload.title,
                    "title",
                    fields,
                ),
                source=get_required_update_value(
                    payload.source,
                    "source",
                    fields,
                ),
                source_url=get_required_update_value(payload.source_url, "source_url", fields),
                description=(payload.description if "description" in fields else UNSET),
                location=(payload.location if "location" in fields else UNSET),
                employment_type=(payload.employment_type if "employment_type" in fields else UNSET),
                discovered_at=(payload.discovered_at if "discovered_at" in fields else UNSET),
            ),
        )
    except UpdateJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except JobSourceURLAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_response(job)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: UUID,
    repository: RepositoryDependency,
) -> None:
    """Delete a job."""

    use_case = DeleteJob(repository)

    try:
        await use_case.execute(job_id)
    except DeleteJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
