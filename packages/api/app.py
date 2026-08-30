from fastapi import FastAPI

from packages.api.middleware.correlation_id import CorrelationIdMiddleware
from packages.api.router import router
from packages.common.exceptions.handlers import (
    unhandled_exception_handler,
)
from packages.common.logging.config import configure_logging

configure_logging()

app = FastAPI(
    title="Job Application Agent API",
    version="0.1.0",
)
app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(router)