import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from packages.common.context.correlation import get_correlation_id

logger = logging.getLogger(__name__)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected application exceptions."""

    correlation_id = get_correlation_id() or "-"

    logger.exception(
        "Unhandled exception while processing request.",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
                "correlation_id": correlation_id,
            },
        },
    )