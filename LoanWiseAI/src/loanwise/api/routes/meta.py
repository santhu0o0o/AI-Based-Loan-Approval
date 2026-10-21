"""Read-only endpoints: ``/api/health``, ``/api/model-info`` and ``/api/sample``."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify

from loanwise.api import messages
from loanwise.api.context import services
from loanwise.api.responses import API_PREFIX, fail, ok
from loanwise.services.model_info import load_model_info
from loanwise.services.sample_service import SampleUnavailableError

bp = Blueprint("meta", __name__, url_prefix=API_PREFIX)


@bp.get("/health")
def health() -> Response:
    """Liveness plus whether a model is loaded."""
    return ok(model_loaded=services().predictions.model_loaded())


@bp.get("/model-info")
def model_info() -> Response | tuple[Response, int]:
    """Return the training report with ``"ok": true`` appended."""
    info = load_model_info(services().settings.model_info_path)
    if info is None:
        return fail(messages.MODEL_INFO_UNAVAILABLE, 503)
    return jsonify({**info, "ok": True})


@bp.get("/sample")
def sample() -> Response | tuple[Response, int]:
    """Return a random demo application, both top-level and under ``"sample"``."""
    try:
        example = services().samples.random_application()
    except SampleUnavailableError:
        return fail(messages.SAMPLE_UNAVAILABLE, 503)
    return ok(**example.fields, sample=example.fields, loan_id=example.loan_id)
