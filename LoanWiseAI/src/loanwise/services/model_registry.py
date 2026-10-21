"""Access to the trained model: lazy, thread-safe loading with hot reload.

:class:`ModelRegistry` loads the joblib pipeline on first use and reloads it
whenever the file's modification time changes, so re-running training updates
a live server without a restart. If the file disappears or a reload fails, the
previously loaded model keeps serving.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import joblib

import loanwise.ml.features  # noqa: F401  (the pickle references functions in this module)

log = logging.getLogger(__name__)


@runtime_checkable
class ProbabilisticClassifier(Protocol):
    """Anything with scikit-learn's ``predict_proba``; column 1 is P(approved)."""

    def predict_proba(self, X: Any) -> Any:
        """Return an ``(n_rows, 2)`` array-like of class probabilities."""


class ModelProvider(Protocol):
    """Source of the current model, or ``None`` when no model is available."""

    def get(self) -> ProbabilisticClassifier | None:
        """Return the model to use for the next prediction."""


class StaticModelProvider:
    """Always returns the same, already-constructed model (tests, embedding)."""

    def __init__(self, model: ProbabilisticClassifier) -> None:
        """Wrap ``model``."""
        self._model = model

    def get(self) -> ProbabilisticClassifier:
        """Return the wrapped model."""
        return self._model


class ModelRegistry:
    """Loads the model file lazily and reloads it when it changes on disk."""

    def __init__(self, path: Path) -> None:
        """Remember ``path``; nothing is loaded until :meth:`get` is called."""
        self.path = path
        self._model: ProbabilisticClassifier | None = None
        self._mtime: float | None = None
        self._lock = threading.Lock()

    def get(self) -> ProbabilisticClassifier | None:
        """Return the current model, loading or reloading it if the file changed."""
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            return self._model  # file gone: keep whatever we had (maybe None)
        if self._is_current(mtime):
            return self._model
        with self._lock:
            if not self._is_current(mtime):
                self._load(mtime)
        return self._model

    def _is_current(self, mtime: float) -> bool:
        """True when a model is loaded and the file has not changed since."""
        return self._model is not None and mtime == self._mtime

    def _load(self, mtime: float) -> None:
        """Load the file, keeping the previous model if anything goes wrong."""
        try:
            model = joblib.load(self.path)
            if not isinstance(model, ProbabilisticClassifier):
                raise TypeError("loaded object has no predict_proba")
        except Exception:
            log.exception("Could not load model from %s", self.path)
            return
        self._model, self._mtime = model, mtime
        log.info("Model loaded from %s", self.path)
