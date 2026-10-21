"""Shared fixtures for unittest-style tests (no pytest conftest needed)."""

from __future__ import annotations

import dataclasses
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from flask import Flask
from flask.testing import FlaskClient

from loanwise.api import create_app
from loanwise.config import Settings

DEFAULT_SETTINGS = Settings.from_env({})  # repo defaults, unaffected by the caller's env
HAS_MODEL = DEFAULT_SETTINGS.model_path.is_file()
SKIP_NO_MODEL = "trained model not built yet (run scripts/train_model.py)"

LEAK_MARKERS = ("Traceback", "Error:", "Exception", "secret internal")


def good_form(**overrides: Any) -> dict[str, Any]:
    """A valid application for a strong applicant; keyword arguments override fields."""
    form: dict[str, Any] = {
        "gender": "Male",
        "married": "Yes",
        "dependents": "0",
        "education": "Graduate",
        "self_employed": "No",
        "applicant_income": 20000,
        "coapplicant_income": 5000,
        "loan_amount": 500000,
        "loan_term": 360,
        "credit_history": "good",
        "property_area": "Urban",
    }
    form.update(overrides)
    return form


def make_settings(tmp: Path, **overrides: Any) -> Settings:
    """Default settings with an isolated database and no built frontend."""
    base = dataclasses.replace(
        DEFAULT_SETTINGS,
        database_path=tmp / "test.db",
        frontend_dist=tmp / "no-dist",
    )
    return dataclasses.replace(base, **overrides)


class FakeModel:
    """Approves when Credit_History == 1 (prob ``p_good``), else rejects (prob ``p_bad``)."""

    def __init__(self, p_good: float = 0.9, p_bad: float = 0.1) -> None:
        self.p_good, self.p_bad = p_good, p_bad
        self.last_frame: pd.DataFrame | None = None

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Record the frame and return fixed probabilities."""
        self.last_frame = X.copy()
        p = np.where(X["Credit_History"].to_numpy() == 1.0, self.p_good, self.p_bad)
        return np.column_stack([1 - p, p])


class BrokenModel:
    """A model whose every prediction raises."""

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Always fail with text that must never reach a user."""
        raise RuntimeError("secret internal traceback text")


class ApiTestCase(unittest.TestCase):
    """Builds an app per test with a temporary database.

    Subclasses set ``model`` to inject a fake (``None`` loads the real model file)
    or override :meth:`settings_overrides`.
    """

    model: Any = None
    app: Flask
    client: FlaskClient
    tmp: Path

    def setUp(self) -> None:
        """Create a temp dir, settings and a test client."""
        self.tmp = Path(tempfile.mkdtemp())
        self.settings = make_settings(self.tmp, **self.settings_overrides())
        self.app = create_app(self.settings, model=self.model)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        """Remove the temp dir."""
        shutil.rmtree(self.tmp, ignore_errors=True)

    def settings_overrides(self) -> dict[str, Any]:
        """Extra :class:`Settings` fields for this test case."""
        return {}

    def assert_friendly(self, body: dict[str, Any]) -> None:
        """Assert an error body is a failure with no technical detail leaked."""
        self.assertFalse(body["ok"])
        text = str(body)
        for leak in LEAK_MARKERS:
            self.assertNotIn(leak, text)
