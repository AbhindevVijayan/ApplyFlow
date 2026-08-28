from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from packages.api.dependencies import AgentOrchestratorDependency
from packages.application.evaluation.evaluate_job import (
    CandidateNotFoundError,
    JobNotFoundError,
)

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


@router.post(
    "/run/{candidate_id}",
    status_code=status.HTTP_200_OK,
)
async def run_agent(
    candidate_id: UUID,
    orchestrator: AgentOrchestratorDependency,
) -> dict[str, object]:
    """Run the complete job discovery and evaluation workflow."""

    try:
        result = await orchestrator.execute(candidate_id)

    except CandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "id": str(result.id),
        "candidate_id": str(result.candidate_id),
        "status": result.status.value,
        "jobs_discovered": result.jobs_discovered,
        "jobs_evaluated": result.jobs_evaluated,
        "applications_created": result.applications_created,
        "started_at": (result.started_at.isoformat() if result.started_at is not None else None),
        "completed_at": (
            result.completed_at.isoformat() if result.completed_at is not None else None
        ),
    }
