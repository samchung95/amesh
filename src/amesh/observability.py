from __future__ import annotations

import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

from prometheus_client import Counter, Info

from amesh import __version__

HTTP_REQUESTS = Counter(
    "amesh_http_requests",
    "AMESH HTTP requests by method, route and status.",
    ("method", "route", "status"),
)
HTTP_REQUEST_DURATION = Counter(
    "amesh_http_request_duration_seconds",
    "Cumulative AMESH HTTP request duration by method and route.",
    ("method", "route"),
)
BUILD_INFO = Info("amesh_build", "AMESH build information.")
BUILD_INFO.info({"version": __version__})


class JsonFormatter(logging.Formatter):
    """Render one stable JSON object per process log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for name in (
            "execution_id",
            "http_method",
            "http_route",
            "http_status",
            "worker_id",
        ):
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def configure_structured_logging(level: str) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["console"], "level": level.upper()},
            "loggers": {
                "uvicorn": {"handlers": ["console"], "level": level.upper(), "propagate": False},
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": level.upper(),
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": level.upper(),
                    "propagate": False,
                },
            },
        }
    )
