from fastapi import FastAPI
from sqlalchemy import text

from packages.database.session import SessionFactory

app = FastAPI(
    title="Job Application Agent API",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, object]:
    database_status = "ok"

    try:
        async with SessionFactory() as session:
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