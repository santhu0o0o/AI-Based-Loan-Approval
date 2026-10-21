"""Error handlers: every failure under ``/api`` becomes a friendly JSON body.

Stack traces and exception text are logged, never returned.
"""

from __future__ import annotations

import logging

from flask import Flask, Response, jsonify, request
from werkzeug.exceptions import HTTPException

from loanwise.api import messages
from loanwise.api.responses import fail, is_api_path
from loanwise.services.prediction_service import (
    InvalidApplicationError,
    ModelPredictionError,
    ModelUnavailableError,
)

log = logging.getLogger(__name__)

ResponseOrError = Response | HTTPException | tuple[Response, int]


def register_error_handlers(app: Flask) -> None:
    """Attach the JSON error handlers to ``app``."""
    app.register_error_handler(InvalidApplicationError, _invalid_application)
    app.register_error_handler(ModelUnavailableError, _model_unavailable)
    app.register_error_handler(ModelPredictionError, _model_failure)
    app.register_error_handler(HTTPException, _http_error)
    app.register_error_handler(Exception, _unhandled)


def _invalid_application(exc: InvalidApplicationError) -> tuple[Response, int]:
    """422 with every field error so the form can highlight them all at once."""
    return jsonify({"ok": False, "errors": exc.errors, "message": messages.FIX_FORM}), 422


def _model_unavailable(_exc: ModelUnavailableError) -> tuple[Response, int]:
    """503 while no trained model is available."""
    return fail(messages.NO_MODEL, 503)


def _model_failure(_exc: ModelPredictionError) -> tuple[Response, int]:
    """500 when the model itself misbehaves (already logged by the service)."""
    return fail(messages.GENERIC_ERROR, 500)


def _http_error(exc: HTTPException) -> ResponseOrError:
    """Plain-English JSON for API routes; Werkzeug's default page elsewhere."""
    code = exc.code or 500
    if is_api_path(request.path):
        return fail(messages.HTTP_ERRORS.get(code, messages.GENERIC_ERROR), code)
    return exc


def _unhandled(exc: Exception) -> ResponseOrError:
    """Log the bug and return a generic message (JSON for the API, HTML for pages)."""
    log.exception("Unhandled error on %s", request.path)
    if is_api_path(request.path):
        return fail(messages.GENERIC_ERROR, 500)
    return Response(messages.PAGE_ERROR_HTML, 500, mimetype="text/html")
