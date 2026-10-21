"""Typed access to the per-app service objects from inside request handlers."""

from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, current_app

from loanwise.config import Settings
from loanwise.services.prediction_service import PredictionService
from loanwise.services.sample_service import SampleService
from loanwise.storage.history_repository import HistoryRepository

_EXTENSION_KEY = "loanwise"


@dataclass(frozen=True)
class AppServices:
    """Everything a blueprint needs, created once per application."""

    settings: Settings
    predictions: PredictionService
    history: HistoryRepository
    samples: SampleService


def attach_services(app: Flask, services: AppServices) -> None:
    """Store ``services`` on ``app`` for later retrieval with :func:`services`."""
    app.extensions[_EXTENSION_KEY] = services


def services() -> AppServices:
    """Return the services of the application handling the current request."""
    found: AppServices = current_app.extensions[_EXTENSION_KEY]
    return found
