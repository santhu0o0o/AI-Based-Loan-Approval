"""Helpers that build the API's JSON envelopes (``{"ok": true|false, ...}``)."""

from __future__ import annotations

from typing import Any

from flask import Response, jsonify

API_PREFIX = "/api"


def ok(**fields: Any) -> Response:
    """Return a 200 response ``{"ok": true, **fields}``."""
    return jsonify({"ok": True, **fields})


def fail(message: str, status: int, **extra: Any) -> tuple[Response, int]:
    """Return an error response ``{"ok": false, "message": ..., **extra}`` with ``status``."""
    return jsonify({"ok": False, "message": message, **extra}), status


def is_api_path(path: str) -> bool:
    """True when ``path`` (a request path starting with ``/``) belongs to the JSON API."""
    return path.startswith(API_PREFIX)
