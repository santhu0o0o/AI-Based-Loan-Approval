"""``GET /api/history`` and ``DELETE /api/history``."""

from __future__ import annotations

from typing import Final

from flask import Blueprint, Response, request

from loanwise.api.context import services
from loanwise.api.responses import API_PREFIX, ok

bp = Blueprint("history", __name__, url_prefix=API_PREFIX)

DEFAULT_LIMIT: Final = 50
MAX_LIMIT: Final = 500


@bp.get("/history")
def list_history() -> Response:
    """Return recent predictions, newest first (``?limit=`` 1-500, default 50)."""
    return ok(items=services().history.list_recent(_requested_limit()))


@bp.delete("/history")
def clear_history() -> Response:
    """Delete every stored prediction."""
    services().history.clear()
    return ok()


def _requested_limit() -> int:
    """Parse ``?limit=``, falling back to the default and clamping to the allowed range."""
    try:
        limit = int(request.args.get("limit", DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return max(1, min(limit, MAX_LIMIT))
