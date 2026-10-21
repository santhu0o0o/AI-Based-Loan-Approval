"""``POST /api/predict``: score one loan application."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, request

from loanwise.api import messages
from loanwise.api.context import services
from loanwise.api.payload import read_payload
from loanwise.api.responses import API_PREFIX, fail

bp = Blueprint("predict", __name__, url_prefix=API_PREFIX)


@bp.post("/predict")
def predict() -> Response | tuple[Response, int]:
    """Validate, score and explain an application.

    Responds 200 with the decision, 400 for an unreadable body, and (through
    :mod:`loanwise.api.errors`) 422 / 503 / 500 for service failures.
    """
    payload, readable = read_payload(request)
    if not readable or not isinstance(payload, dict):
        return fail(messages.BAD_JSON, 400)
    result = services().predictions.predict(payload)
    return jsonify(result.to_response())
