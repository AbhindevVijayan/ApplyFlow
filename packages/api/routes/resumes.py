from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.schemas import CreateResumeRequest, ResumeResponse
from packages.application.resumes.create_resume import (
    CreateResume,
    CreateResumeCommand,
)
from packages.application.resumes.get_resume import (
    GetResume,
    GetResumeCommand,
)
from packages.database.repositories.resume_adapter import (
    ResumeRepositoryAdapter,
)
from packages.database.session import get_session
from packages.domain.resumes.entities import Resume

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
)


SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


def get_resume_repository(
    session: SessionDependency,
) -> ResumeRepositoryAdapter:
    """Build the resume repository for the current request."""
    return ResumeRepositoryAdapter(session)


RepositoryDependency = Annotated[
    ResumeRepositoryAdapter,
    Depends(get_resume_repository),
]


@router.post(
    "",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_resume(
    payload: CreateResumeRequest,
    repository: RepositoryDependency,
) -> ResumeResponse:
    """Create a resume."""

    use_case = CreateResume(repository)

    resume = await use_case.execute(
        CreateResumeCommand(
            candidate_id=payload.candidate_id,
            filename=payload.filename,
            content_type=payload.content_type,
            storage_key=payload.storage_key,
            parsed_text=payload.parsed_text,
            is_canonical=payload.is_canonical,
        ),
    )

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        content_type=resume.content_type,
        storage_key=resume.storage_key,
        parsed_text=resume.parsed_text,
        is_canonical=resume.is_canonical,
        created_at=resume.created_at,
    )


@router.get(
    "/candidate/{candidate_id}/canonical",
    response_model=ResumeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_canonical_resume(
    candidate_id: UUID,
    repository: RepositoryDependency,
) -> ResumeResponse:
    """Return the canonical resume for a candidate."""

    use_case = GetResume(repository)

    resume = await use_case.execute(
        GetResumeCommand(
            candidate_id=candidate_id,
            canonical_only=True,
        ),
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"No canonical resume found for candidate {candidate_id}."),
        )
    if not isinstance(resume, Resume):
        raise TypeError("Expected a single resume.")

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        content_type=resume.content_type,
        storage_key=resume.storage_key,
        parsed_text=resume.parsed_text,
        is_canonical=resume.is_canonical,
        created_at=resume.created_at,
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_resume(
    resume_id: UUID,
    repository: RepositoryDependency,
) -> ResumeResponse:
    """Return a resume by ID."""

    use_case = GetResume(repository)

    resume = await use_case.execute(
        GetResumeCommand(
            resume_id=resume_id,
        ),
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume {resume_id} not found.",
        )

    if not isinstance(resume, Resume):
        raise TypeError("Expected a single resume.")

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        content_type=resume.content_type,
        storage_key=resume.storage_key,
        parsed_text=resume.parsed_text,
        is_canonical=resume.is_canonical,
        created_at=resume.created_at,
    )


@router.get(
    "/candidate/{candidate_id}",
    response_model=list[ResumeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_candidate_resumes(
    candidate_id: UUID,
    repository: RepositoryDependency,
) -> list[ResumeResponse]:
    """Return all resumes belonging to a candidate."""

    use_case = GetResume(repository)

    resumes = await use_case.execute(
        GetResumeCommand(
            candidate_id=candidate_id,
        ),
    )
    if not isinstance(resumes, list):
        raise TypeError("Expected a list of resumes.")

    return [
        ResumeResponse(
            id=resume.id,
            candidate_id=resume.candidate_id,
            filename=resume.filename,
            content_type=resume.content_type,
            storage_key=resume.storage_key,
            parsed_text=resume.parsed_text,
            is_canonical=resume.is_canonical,
            created_at=resume.created_at,
        )
        for resume in resumes
    ]
