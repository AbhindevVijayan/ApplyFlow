from fastapi import FastAPI

from packages.api.router import router

app = FastAPI(
    title="Job Application Agent API",
    version="0.1.0",
)

app.include_router(router)
