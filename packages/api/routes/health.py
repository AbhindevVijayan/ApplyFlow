from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def health_check(
    session: AsyncSession,
) -> dict[str, object]:
    database_status = "ok"

    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    overall_status = "ok" if database_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "services": {
            "api": "ok",
            "database": database_status,
        },
    }
