"""Read the training report (``model_info.json``) written by :mod:`loanwise.ml.train`."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def load_model_info(path: Path) -> dict[str, Any] | None:
    """Return the report as a dict, or ``None`` if it is missing or unreadable.

    A valid JSON document that is not an object is wrapped as ``{"data": ...}``
    so callers can always merge extra keys into the result.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            info = json.load(fh)
    except (OSError, ValueError):
        log.warning("Model info not available at %s", path)
        return None
    return info if isinstance(info, dict) else {"data": info}
