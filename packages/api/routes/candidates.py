from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.schemas import (
    CandidateResponse,
    CreateCandidateRequest,
    UpdateCandidateRequest,
)
from packages.application.candidates.create_candidate import (
    CandidateAlreadyExistsError,
    CreateCandidate,
    CreateCandidateCommand,
)
from packages.application.candidates.delete_candidate import (
    CandidateNotFoundError as DeleteCandidateNotFoundError,
)
from packages.application.candidates.delete_candidate import (
    DeleteCandidate,
)
from packages.application.candidates.get_candidate import (
    CandidateNotFoundError as GetCandidateNotFoundError,
)
from packages.application.candidates.get_candidate import (
    GetCandidate,
)
from packages.application.candidates.update_candidate import (
    UNSET,
    CandidateEmailAlreadyExistsError,
    Unset,
    UpdateCandidate,
    UpdateCandidateCommand,
)
from packages.application.candidates.update_candidate import (
    CandidateNotFoundError as UpdateCandidateNotFoundError,
)
from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.database.session import get_session

router = APIRouter(
    prefix="/candidates",
    tags=["candidates"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


def get_candidate_repository(
    session: SessionDependency,
) -> CandidateRepositoryAdapter:
    """Build the candidate repository for the current request."""
    return CandidateRepositoryAdapter(session)


RepositoryDependency = Annotated[
    CandidateRepositoryAdapter,
    Depends(get_candidate_repository),
]


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate(
    payload: CreateCandidateRequest,
    repository: RepositoryDependency,
) -> CandidateResponse:
    """Create a candidate."""

    use_case = CreateCandidate(repository)

    try:
        candidate = await use_case.execute(
            CreateCandidateCommand(
                full_name=payload.full_name,
                email=str(payload.email),
                phone=payload.phone,
                location=payload.location,
            ),
        )
    except CandidateAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return CandidateResponse(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
    )


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
async def get_candidate(
    candidate_id: UUID,
    repository: RepositoryDependency,
) -> CandidateResponse:
    """Retrieve a candidate."""

    use_case = GetCandidate(repository)

    try:
        candidate = await use_case.execute(candidate_id)
    except GetCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CandidateResponse(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
    )


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
    "/{candidate_id}",
    response_model=CandidateResponse,
)
async def update_candidate(
    candidate_id: UUID,
    payload: UpdateCandidateRequest,
    repository: CandidateRepositoryAdapter = Depends(  # noqa: B008
        get_candidate_repository,
    ),
) -> CandidateResponse:
    """Partially update a candidate."""

    fields = payload.model_fields_set

    use_case = UpdateCandidate(repository)

    try:
        candidate = await use_case.execute(
            UpdateCandidateCommand(
                candidate_id=candidate_id,
                full_name=get_required_update_value(
                    payload.full_name,
                    "full_name",
                    fields,
                ),
                email=get_required_update_value(
                    str(payload.email) if "email" in fields and payload.email is not None else None,
                    "email",
                    fields,
                ),
                phone=(payload.phone if "phone" in fields else UNSET),
                location=(payload.location if "location" in fields else UNSET),
            ),
        )
    except UpdateCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CandidateEmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return CandidateResponse(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
    )


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_candidate(
    candidate_id: UUID,
    repository: RepositoryDependency,
) -> None:
    """Delete a candidate."""

    use_case = DeleteCandidate(repository)

    try:
        await use_case.execute(candidate_id)
    except DeleteCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
