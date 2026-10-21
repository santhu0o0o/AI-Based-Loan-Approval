"""Flask application factory.

Usage::

    from loanwise.api import create_app
    app = create_app()                      # settings from LOANWISE_* env vars
    app = create_app(settings, model=fake)  # tests: inject any predict_proba object
"""

from __future__ import annotations

from urllib.parse import urlsplit

from flask import Flask, Response, request

from loanwise.api.context import AppServices, attach_services
from loanwise.api.errors import register_error_handlers
from loanwise.api.routes import API_BLUEPRINTS
from loanwise.api.spa import bp as spa_blueprint
from loanwise.config import Settings
from loanwise.services.model_registry import (
    ModelProvider,
    ModelRegistry,
    ProbabilisticClassifier,
    StaticModelProvider,
)
from loanwise.services.prediction_service import PredictionService
from loanwise.services.sample_service import SampleService
from loanwise.storage.history_repository import HistoryRepository

__all__ = ["create_app", "is_allowed_origin"]

_CORS_METHODS = "GET, POST, DELETE, OPTIONS"
_CORS_HEADERS = "Content-Type"


def create_app(
    settings: Settings | None = None, *, model: ProbabilisticClassifier | None = None
) -> Flask:
    """Build a fully wired Flask application.

    Args:
        settings: configuration; defaults to :meth:`Settings.from_env`.
        model: optional ready-made model to use instead of loading
            ``settings.model_path`` (intended for tests).
    """
    settings = settings or Settings.from_env()
    app = Flask(__name__, static_folder=None)
    app.config.update(MAX_CONTENT_LENGTH=settings.max_request_bytes)
    app.json.ensure_ascii = False  # type: ignore[attr-defined]
    app.json.sort_keys = False  # type: ignore[attr-defined]

    attach_services(app, _build_services(settings, model))
    for blueprint in API_BLUEPRINTS:
        app.register_blueprint(blueprint)
    app.register_blueprint(spa_blueprint)  # last: its catch-all route must not shadow the API
    register_error_handlers(app)
    _register_response_headers(app, settings.cors_origins)
    return app


def _build_services(settings: Settings, model: ProbabilisticClassifier | None) -> AppServices:
    """Instantiate the service graph for one application."""
    models: ModelProvider = (
        StaticModelProvider(model) if model is not None else ModelRegistry(settings.model_path)
    )
    history = HistoryRepository(settings.database_path)
    return AppServices(
        settings=settings,
        predictions=PredictionService(models, history),
        history=history,
        samples=SampleService(settings.sample_data_path),
    )


def is_allowed_origin(origin: str, allowed: tuple[str, ...]) -> bool:
    """Return True if ``origin``'s scheme and host exactly match an allowed entry.

    Any port is accepted (dev servers move around), but the hostname must match
    exactly, so look-alikes such as ``http://localhost.evil.com`` are rejected.
    """
    if not origin or not allowed:
        return False
    try:
        parsed = urlsplit(origin)
        parsed.port  # noqa: B018 - raises ValueError on a malformed port
    except ValueError:
        return False
    if not parsed.scheme or not parsed.hostname or parsed.path not in ("", "/"):
        return False
    return f"{parsed.scheme}://{parsed.hostname}" in {a.rstrip("/").lower() for a in allowed}


def _register_response_headers(app: Flask, cors_origins: tuple[str, ...]) -> None:
    """Add CORS headers for allowed dev origins on /api/*, and ``nosniff`` everywhere."""

    @app.after_request
    def add_headers(resp: Response) -> Response:
        origin = request.headers.get("Origin", "")
        if request.path.startswith("/api/") and is_allowed_origin(origin, cors_origins):
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Methods"] = _CORS_METHODS
            resp.headers["Access-Control-Allow-Headers"] = _CORS_HEADERS
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        return resp
