from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.schemas import (
    ApplicationResponse,
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from packages.application.applications.create_application import (
    ApplicationAlreadyExistsError,
    CreateApplication,
    CreateApplicationCommand,
)
from packages.application.applications.delete_application import (
    ApplicationNotFoundError as DeleteApplicationNotFoundError,
)
from packages.application.applications.delete_application import (
    DeleteApplication,
)
from packages.application.applications.get_application import (
    ApplicationNotFoundError as GetApplicationNotFoundError,
)
from packages.application.applications.get_application import (
    GetApplication,
)
from packages.application.applications.list_applications import ListApplications
from packages.application.applications.update_application import (
    UNSET,
    InvalidApplicationTransitionError,
    UpdateApplication,
    UpdateApplicationCommand,
)
from packages.application.applications.update_application import (
    ApplicationNotFoundError as UpdateApplicationNotFoundError,
)
from packages.database.repositories.application_adapter import (
    ApplicationRepositoryAdapter,
)
from packages.database.session import get_session
from packages.domain.applications.entities import Application

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)


SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


def get_application_repository(
    session: SessionDependency,
) -> ApplicationRepositoryAdapter:
    """Build the application repository for the current request."""

    return ApplicationRepositoryAdapter(session)


RepositoryDependency = Annotated[
    ApplicationRepositoryAdapter,
    Depends(get_application_repository),
]


def to_response(
    application: Application,
) -> ApplicationResponse:
    """Convert a domain application into an HTTP response."""

    return ApplicationResponse(
        id=application.id,
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status,
        applied_at=application.applied_at,
        external_application_url=application.external_application_url,
        notes=application.notes,
        failure_reason=application.failure_reason,
        created_at=application.created_at,
        updated_at=application.updated_at,
    )


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    payload: CreateApplicationRequest,
    repository: RepositoryDependency,
) -> ApplicationResponse:
    """Create a job application."""

    use_case = CreateApplication(repository)

    try:
        application = await use_case.execute(
            CreateApplicationCommand(
                candidate_id=payload.candidate_id,
                job_id=payload.job_id,
                resume_id=payload.resume_id,
                status=payload.status,
                applied_at=payload.applied_at,
                external_application_url=payload.external_application_url,
                notes=payload.notes,
                failure_reason=payload.failure_reason,
            ),
        )
    except ApplicationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_response(application)


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_application(
    application_id: UUID,
    repository: RepositoryDependency,
) -> ApplicationResponse:
    """Return an application by ID."""

    use_case = GetApplication(repository)

    try:
        application = await use_case.execute(application_id)
    except GetApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return to_response(application)


@router.get(
    "/candidate/{candidate_id}",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
)
async def list_candidate_applications(
    candidate_id: UUID,
    repository: RepositoryDependency,
) -> list[ApplicationResponse]:
    """Return all applications belonging to a candidate."""

    use_case = ListApplications(repository)

    applications = await use_case.by_candidate(candidate_id)

    return [to_response(application) for application in applications]


@router.get(
    "/job/{job_id}",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
)
async def list_job_applications(
    job_id: UUID,
    repository: RepositoryDependency,
) -> list[ApplicationResponse]:
    """Return all applications for a job."""

    use_case = ListApplications(repository)

    applications = await use_case.by_job(job_id)

    return [to_response(application) for application in applications]


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_application(
    application_id: UUID,
    payload: UpdateApplicationRequest,
    repository: RepositoryDependency,
) -> ApplicationResponse:
    """Partially update an application."""

    fields = payload.model_fields_set

    use_case = UpdateApplication(repository)

    try:
        application = await use_case.execute(
            UpdateApplicationCommand(
                application_id=application_id,
                status=(payload.status if "status" in fields else UNSET),
                applied_at=(payload.applied_at if "applied_at" in fields else UNSET),
                external_application_url=(
                    payload.external_application_url
                    if "external_application_url" in fields
                    else UNSET
                ),
                notes=(payload.notes if "notes" in fields else UNSET),
                failure_reason=(payload.failure_reason if "failure_reason" in fields else UNSET),
            ),
        )
    except UpdateApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidApplicationTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_response(application)


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_application(
    application_id: UUID,
    repository: RepositoryDependency,
) -> None:
    """Delete an application."""

    use_case = DeleteApplication(repository)

    try:
        await use_case.execute(application_id)
    except DeleteApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
