"""Configure structured JSON logging."""

import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
        }

        for key in (
            "request_id",
            "records",
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with the JSON formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
