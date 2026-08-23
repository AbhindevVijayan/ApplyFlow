from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.api.routes.applications import router as applications_router
from packages.api.routes.candidates import router as candidates_router
from packages.api.routes.discovery import router as discovery_router
from packages.api.routes.health import health_check
from packages.api.routes.jobs import router as jobs_router
from packages.api.routes.resumes import router as resumes_router
from packages.api.routes.skills import router as skills_router
from packages.database.session import get_session

router = APIRouter()

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.get("/health", tags=["health"])
async def health(
    session: SessionDependency,
) -> dict[str, object]:
    return await health_check(session)


router.include_router(candidates_router)
router.include_router(resumes_router)
router.include_router(jobs_router)
router.include_router(discovery_router)
router.include_router(skills_router)
router.include_router(applications_router)
