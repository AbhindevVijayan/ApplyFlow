from contextvars import ContextVar

correlation_id_context: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)


def get_correlation_id() -> str | None:
    """Return the correlation ID for the current execution context."""

    return correlation_id_context.get()


def set_correlation_id(
    correlation_id: str,
):
    """Set the correlation ID for the current execution context."""

    return correlation_id_context.set(correlation_id)


def reset_correlation_id(token) -> None:
    """Reset the correlation ID to its previous value."""

    correlation_id_context.reset(token)