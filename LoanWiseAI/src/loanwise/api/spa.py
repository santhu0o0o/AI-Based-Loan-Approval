"""Serves the built React single-page app from ``frontend/dist``.

Any path that is not an existing file falls back to ``index.html`` so client-side
routes work on refresh. Unknown ``/api/*`` paths never fall back: they return
JSON 404 (or 405 when the path exists for another method). Until the frontend
has been built, a short "almost ready" page is served instead.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, current_app, send_from_directory
from werkzeug.exceptions import HTTPException

from loanwise.api import messages
from loanwise.api.context import services
from loanwise.api.responses import fail

bp = Blueprint("spa", __name__)

_INDEX = "index.html"
_PROBE_METHODS = ("GET", "POST", "DELETE")


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def serve(path: str) -> Response | tuple[Response, int]:
    """Serve a static asset, ``index.html`` or the API's JSON 404/405."""
    if path == "api" or path.startswith("api/"):
        return _api_miss(path)
    dist = services().settings.frontend_dist
    if not (dist / _INDEX).is_file():
        return Response(messages.FRONTEND_MISSING_HTML, 200, mimetype="text/html")
    if path and _is_file_inside(dist, path):
        return send_from_directory(dist, path)
    return send_from_directory(dist, _INDEX)


def _api_miss(path: str) -> tuple[Response, int]:
    """405 if ``/path`` is a real API route for another method, otherwise 404."""
    adapter = current_app.url_map.bind("localhost")
    for method in _PROBE_METHODS:
        try:
            endpoint, _ = adapter.match("/" + path, method=method)
        except HTTPException:
            continue
        if endpoint != f"{bp.name}.serve":
            return fail(messages.HTTP_ERRORS[405], 405)
    return fail(messages.HTTP_ERRORS[404], 404)


def _is_file_inside(root: Path, relative: str) -> bool:
    """True when ``root/relative`` is an existing file that does not escape ``root``."""
    real_root = root.resolve()
    target = (root / relative).resolve()
    return target.is_relative_to(real_root) and target != real_root and target.is_file()
