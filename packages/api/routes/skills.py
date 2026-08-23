from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.schemas import (
    AddCandidateSkillRequest,
    CandidateSkillResponse,
    CreateSkillRequest,
    SkillResponse,
)
from packages.application.skills.add_candidate_skill import (
    AddCandidateSkill,
    AddCandidateSkillCommand,
    CandidateSkillAlreadyExistsError,
)
from packages.application.skills.add_candidate_skill import (
    CandidateNotFoundError as AddCandidateSkillCandidateNotFoundError,
)
from packages.application.skills.add_candidate_skill import (
    SkillNotFoundError as AddCandidateSkillNotFoundError,
)
from packages.application.skills.create_skill import (
    CreateSkill,
    CreateSkillCommand,
    SkillAlreadyExistsError,
)
from packages.application.skills.delete_skill import (
    DeleteSkill,
)
from packages.application.skills.delete_skill import (
    SkillNotFoundError as DeleteSkillNotFoundError,
)
from packages.application.skills.get_candidate_skills import (
    CandidateNotFoundError as GetCandidateSkillsCandidateNotFoundError,
)
from packages.application.skills.get_candidate_skills import (
    GetCandidateSkills,
)
from packages.application.skills.get_skill import (
    GetSkill,
)
from packages.application.skills.get_skill import (
    SkillNotFoundError as GetSkillNotFoundError,
)
from packages.application.skills.list_skills import ListSkills
from packages.application.skills.remove_candidate_skill import (
    CandidateNotFoundError as RemoveCandidateSkillCandidateNotFoundError,
)
from packages.application.skills.remove_candidate_skill import (
    CandidateSkillNotFoundError,
    RemoveCandidateSkill,
)
from packages.application.skills.remove_candidate_skill import (
    SkillNotFoundError as RemoveCandidateSkillNotFoundError,
)
from packages.application.skills.update_candidate_skill import (
    CandidateNotFoundError as UpdateCandidateSkillCandidateNotFoundError,
)
from packages.application.skills.update_candidate_skill import (
    CandidateSkillNotFoundError as UpdateCandidateSkillAssociationNotFoundError,
)
from packages.application.skills.update_candidate_skill import (
    SkillNotFoundError as UpdateCandidateSkillSkillNotFoundError,
)
from packages.application.skills.update_candidate_skill import (
    UpdateCandidateSkill,
    UpdateCandidateSkillCommand,
)
from packages.database.repositories.candidate_adapter import (
    CandidateRepositoryAdapter,
)
from packages.database.repositories.skill_adapter import (
    SkillRepositoryAdapter,
)
from packages.database.session import get_session
from packages.domain.skills.entities import CandidateSkill, Skill

router = APIRouter(
    prefix="/skills",
    tags=["skills"],
)


SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


def get_skill_repository(
    session: SessionDependency,
) -> SkillRepositoryAdapter:
    """Build the skill repository for the current request."""
    return SkillRepositoryAdapter(session)


def get_candidate_repository(
    session: SessionDependency,
) -> CandidateRepositoryAdapter:
    """Build the candidate repository for the current request."""
    return CandidateRepositoryAdapter(session)


SkillRepositoryDependency = Annotated[
    SkillRepositoryAdapter,
    Depends(get_skill_repository),
]

CandidateRepositoryDependency = Annotated[
    CandidateRepositoryAdapter,
    Depends(get_candidate_repository),
]


def to_skill_response(skill: Skill) -> SkillResponse:
    """Convert a domain skill into an HTTP response."""
    return SkillResponse(
        id=skill.id,
        name=skill.name,
    )


def to_candidate_skill_response(
    candidate_skill: CandidateSkill,
) -> CandidateSkillResponse:
    """Convert a candidate-skill entity into an HTTP response."""
    return CandidateSkillResponse(
        candidate_id=candidate_skill.candidate_id,
        skill_id=candidate_skill.skill_id,
        proficiency=candidate_skill.proficiency,
    )


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    payload: CreateSkillRequest,
    repository: SkillRepositoryDependency,
) -> SkillResponse:
    """Create a skill."""

    use_case = CreateSkill(repository)

    try:
        skill = await use_case.execute(
            CreateSkillCommand(
                name=payload.name,
            ),
        )
    except SkillAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_skill_response(skill)


@router.get(
    "",
    response_model=list[SkillResponse],
    status_code=status.HTTP_200_OK,
)
async def list_skills(
    repository: SkillRepositoryDependency,
) -> list[SkillResponse]:
    """Return all skills."""

    use_case = ListSkills(repository)

    skills = await use_case.execute()

    return [to_skill_response(skill) for skill in skills]


@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
    status_code=status.HTTP_200_OK,
)
async def get_skill(
    skill_id: UUID,
    repository: SkillRepositoryDependency,
) -> SkillResponse:
    """Return a skill by ID."""

    use_case = GetSkill(repository)

    try:
        skill = await use_case.execute(skill_id)
    except GetSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return to_skill_response(skill)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_skill(
    skill_id: UUID,
    repository: SkillRepositoryDependency,
) -> None:
    """Delete a skill."""

    use_case = DeleteSkill(repository)

    try:
        await use_case.execute(skill_id)
    except DeleteSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/candidates/{candidate_id}",
    response_model=CandidateSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_candidate_skill(
    candidate_id: UUID,
    payload: AddCandidateSkillRequest,
    skill_repository: SkillRepositoryDependency,
    candidate_repository: CandidateRepositoryDependency,
) -> CandidateSkillResponse:
    """Assign a skill to a candidate."""

    use_case = AddCandidateSkill(
        skill_repository=skill_repository,
        candidate_repository=candidate_repository,
    )

    try:
        candidate_skill = await use_case.execute(
            AddCandidateSkillCommand(
                candidate_id=candidate_id,
                skill_id=payload.skill_id,
                proficiency=payload.proficiency,
            ),
        )
    except AddCandidateSkillCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AddCandidateSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CandidateSkillAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return to_candidate_skill_response(candidate_skill)


@router.get(
    "/candidates/{candidate_id}",
    response_model=list[CandidateSkillResponse],
    status_code=status.HTTP_200_OK,
)
async def get_candidate_skills(
    candidate_id: UUID,
    skill_repository: SkillRepositoryDependency,
    candidate_repository: CandidateRepositoryDependency,
) -> list[CandidateSkillResponse]:
    """Return all skills assigned to a candidate."""

    use_case = GetCandidateSkills(
        skill_repository=skill_repository,
        candidate_repository=candidate_repository,
    )

    try:
        candidate_skills = await use_case.execute(candidate_id)
    except GetCandidateSkillsCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [to_candidate_skill_response(candidate_skill) for candidate_skill in candidate_skills]


@router.patch(
    "/candidates/{candidate_id}/{skill_id}",
    response_model=CandidateSkillResponse,
    status_code=status.HTTP_200_OK,
)
async def update_candidate_skill(
    candidate_id: UUID,
    skill_id: UUID,
    payload: AddCandidateSkillRequest,
    skill_repository: SkillRepositoryDependency,
    candidate_repository: CandidateRepositoryDependency,
) -> CandidateSkillResponse:
    """Update a candidate skill's proficiency."""

    use_case = UpdateCandidateSkill(
        skill_repository=skill_repository,
        candidate_repository=candidate_repository,
    )

    try:
        candidate_skill = await use_case.execute(
            UpdateCandidateSkillCommand(
                candidate_id=candidate_id,
                skill_id=skill_id,
                proficiency=payload.proficiency,
            ),
        )
    except UpdateCandidateSkillCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UpdateCandidateSkillSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UpdateCandidateSkillAssociationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return to_candidate_skill_response(candidate_skill)


@router.delete(
    "/candidates/{candidate_id}/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_candidate_skill(
    candidate_id: UUID,
    skill_id: UUID,
    skill_repository: SkillRepositoryDependency,
    candidate_repository: CandidateRepositoryDependency,
) -> None:
    """Remove a skill from a candidate."""

    use_case = RemoveCandidateSkill(
        skill_repository=skill_repository,
        candidate_repository=candidate_repository,
    )

    try:
        await use_case.execute(
            candidate_id=candidate_id,
            skill_id=skill_id,
        )
    except RemoveCandidateSkillCandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RemoveCandidateSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CandidateSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
