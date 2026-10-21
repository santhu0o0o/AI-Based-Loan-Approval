"""Process-wide logging setup (plain text for humans, JSON lines for log shippers).

Library modules only ever call ``logging.getLogger(__name__)``; entry points
(``wsgi.py``, the dev server and the training CLI) call :func:`configure_logging`
exactly once at start-up.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

TEXT_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


class JsonFormatter(logging.Formatter):
    """Render each record as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialise ``record`` (and any exception traceback) to a JSON string."""
        payload: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """Install a single stderr handler on the root logger.

    Args:
        level: standard level name such as ``"INFO"`` or ``"DEBUG"``.
        fmt: ``"json"`` for structured output, anything else for plain text.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if fmt == "json" else logging.Formatter(TEXT_FORMAT))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
