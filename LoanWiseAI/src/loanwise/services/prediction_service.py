"""Use case "check my loan": validate -> sanitise -> predict -> guardrails -> persist.

The service knows nothing about HTTP. Failures are reported as exceptions that
the API layer maps to status codes (see :mod:`loanwise.api.errors`).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

from loanwise.domain.guardrails import Decision, apply_guardrails
from loanwise.domain.sanitizer import to_model_frame
from loanwise.domain.validation import validate_application
from loanwise.services.model_registry import ModelProvider, ProbabilisticClassifier
from loanwise.storage.history_repository import HistoryRepository

log = logging.getLogger(__name__)


class PredictionError(Exception):
    """Base class for the ways a prediction request can fail."""


class InvalidApplicationError(PredictionError):
    """The answers failed validation; ``errors`` maps field -> message."""

    def __init__(self, errors: dict[str, str]) -> None:
        """Keep the per-field messages for the response body."""
        super().__init__(f"{len(errors)} invalid field(s)")
        self.errors = errors


class ModelUnavailableError(PredictionError):
    """No trained model could be loaded."""


class ModelPredictionError(PredictionError):
    """The model raised or returned an unusable probability."""


@dataclass
class PredictionResult:
    """Everything returned to the applicant for one successful prediction."""

    decision: Decision
    warnings: list[str] = field(default_factory=list)
    id: int | None = None

    def to_response(self) -> dict[str, Any]:
        """Serialise in the documented field order of ``POST /api/predict``."""
        body = self._public_fields()
        body["id"] = self.id
        return body

    def to_record(self) -> dict[str, Any]:
        """Serialise for the history table (adds the raw model probability)."""
        return {**self._public_fields(), "model_probability": self.decision.approval_probability}

    def _public_fields(self) -> dict[str, Any]:
        """Fields shared by the HTTP response and the stored history record."""
        d = self.decision
        return {
            "ok": True,
            "approved": d.approved,
            "verdict": d.verdict,
            "headline": d.headline,
            "confidence": d.confidence,
            "confidence_label": d.confidence_label,
            "reasons": d.reasons,
            "warnings": self.warnings,
            "guardrail_applied": d.guardrail_applied,
            "emi_estimate": d.emi_estimate,
        }


class PredictionService:
    """Runs a loan application through every layer and records the outcome."""

    def __init__(self, models: ModelProvider, history: HistoryRepository) -> None:
        """Wire the service to a model source and a history store."""
        self._models = models
        self._history = history

    def model_loaded(self) -> bool:
        """True when a model is available for predictions."""
        return self._models.get() is not None

    def predict(self, payload: dict[str, Any]) -> PredictionResult:
        """Score one application.

        Raises:
            InvalidApplicationError: if any answer fails validation (checked first,
                so applicants get feedback even when no model is loaded).
            ModelUnavailableError: if no model is loaded.
            ModelPredictionError: if the model errors or returns a non-finite probability.
        """
        checked = validate_application(payload)
        if not checked.ok:
            raise InvalidApplicationError(checked.errors)
        model = self._models.get()
        if model is None:
            raise ModelUnavailableError
        sanitized = to_model_frame(checked.cleaned)
        p_approve = _approval_probability(model, sanitized.frame)
        result = PredictionResult(
            decision=apply_guardrails(checked.cleaned, p_approve),
            warnings=checked.warnings + sanitized.warnings,
        )
        result.id = self._save(checked.cleaned, result)
        return result

    def _save(self, cleaned: dict[str, Any], result: PredictionResult) -> int | None:
        """Persist the prediction; history is nice-to-have, so failures only log."""
        try:
            return self._history.add(
                cleaned,
                approved=result.decision.approved,
                verdict=result.decision.verdict,
                confidence=result.decision.confidence,
                result=result.to_record(),
            )
        except Exception:
            log.exception("Could not save prediction history")
            return None


def _approval_probability(model: ProbabilisticClassifier, frame: Any) -> float:
    """Return P(approved) for the single row in ``frame``.

    Raises:
        ModelPredictionError: on any model error or a NaN/infinite probability.
    """
    try:
        p_approve = float(model.predict_proba(frame)[0][1])
    except Exception as exc:
        log.exception("Model prediction failed")
        raise ModelPredictionError from exc
    if not math.isfinite(p_approve):
        log.error("Model returned a non-finite probability: %r", p_approve)
        raise ModelPredictionError
    return p_approve
