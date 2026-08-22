from typing import Annotated

from fastapi import APIRouter, Depends

from packages.api.dependencies import get_discovery_use_case
from packages.application.discovery.run_discovery import RunDiscovery
from packages.config.settings import get_settings

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"],
)


DiscoveryDependency = Annotated[
    RunDiscovery,
    Depends(get_discovery_use_case),
]


@router.post(
    "/run",
    status_code=200,
)
async def discover_jobs(
    use_case: DiscoveryDependency,
) -> dict[str, object]:
    """Run job discovery across configured external sources."""

    settings = get_settings()

    if not settings.greenhouse_enabled:
        return {
            "status": "disabled",
            "sources": [],
            "jobs_discovered": 0,
        }

    results = await use_case.execute()

    return {
        "status": "completed",
        "sources": [
            {
                "source": result.source,
                "jobs_discovered": len(result.jobs),
            }
            for result in results
        ],
        "jobs_discovered": sum(len(result.jobs) for result in results),
    }
