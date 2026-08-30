import logging
import sys

from packages.common.context.correlation import get_correlation_id


class CorrelationIdFilter(logging.Filter):
    """Attach the current correlation ID to log records."""

    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:
        record.correlation_id = get_correlation_id() or "-"
        return True


def configure_logging() -> None:
    """Configure application-wide logging."""

    handler = logging.StreamHandler(sys.stdout)

    handler.addFilter(CorrelationIdFilter())

    formatter = logging.Formatter(
        (
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "[correlation_id=%(correlation_id)s] "
            "%(message)s"
        ),
    )

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)