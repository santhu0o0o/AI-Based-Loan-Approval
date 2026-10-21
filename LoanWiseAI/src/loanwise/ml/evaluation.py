"""Model evaluation: hold-out metrics, cross-validation, selection and sanity checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, TypedDict

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline

from loanwise.ml.features import friendly_name
from loanwise.ml.pipelines import RANDOM_STATE, model_candidates

TEST_SIZE: Final = 0.2
CV_FOLDS: Final = 5
SELECTION_TIE_TOLERANCE: Final = 0.001
TOP_FEATURES: Final = 8

# The hold-out split is used only for reporting, never for choosing, so its
# scores stay an honest estimate. Selection uses CV on the training split.
SELECTION_RULE: Final = (
    "Highest mean 5-fold CV accuracy on the training split (hold-out test set is "
    "used only for reporting); ties within 0.001 go to the lower CV std."
)


class ModelMetrics(TypedDict):
    """Per-model scores as stored in ``model_info.json``."""

    name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    cv_accuracy_mean: float
    cv_accuracy_std: float


class FeatureImportance(TypedDict):
    """One readable feature and its normalised importance."""

    feature: str
    importance: float


@dataclass(frozen=True)
class FittedModel:
    """The tuned pipeline for one candidate and the grid-search winner's parameters."""

    pipeline: Pipeline
    best_params: dict[str, Any]


@dataclass(frozen=True)
class EvaluationReport:
    """Results of :func:`evaluate_models`."""

    metrics: list[ModelMetrics]
    fitted: dict[str, FittedModel]
    baseline_accuracy: float  # always predicting "approved" on the hold-out set


@dataclass(frozen=True)
class SweepResult:
    """One passed monotonicity sweep: approval probability at both ends."""

    profile: int
    label: str
    p_start: float
    p_end: float


class MonotonicityError(AssertionError):
    """The model's approval probability moved the wrong way in a sweep."""


def evaluate_models(X: pd.DataFrame, y: pd.Series) -> EvaluationReport:
    """Tune every candidate with CV on an 80% split and score it on the 20% hold-out."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    metrics: list[ModelMetrics] = []
    fitted: dict[str, FittedModel] = {}
    for candidate in model_candidates(X):
        search = GridSearchCV(
            candidate.pipeline, candidate.param_grid, cv=cv, scoring="accuracy", n_jobs=-1
        )
        search.fit(X_train, y_train)
        best: Pipeline = search.best_estimator_
        cv_scores = cross_val_score(best, X_train, y_train, cv=cv, scoring="accuracy")
        metrics.append(_score(candidate.name, y_test, best.predict(X_test), cv_scores))
        fitted[candidate.name] = FittedModel(best, dict(search.best_params_))
    return EvaluationReport(metrics, fitted, baseline_accuracy=float(y_test.mean()))


def choose_model(metrics: list[ModelMetrics]) -> str:
    """Apply :data:`SELECTION_RULE` and return the winning model's name."""
    best_cv = max(m["cv_accuracy_mean"] for m in metrics)
    contenders = [m for m in metrics if best_cv - m["cv_accuracy_mean"] <= SELECTION_TIE_TOLERANCE]
    return min(contenders, key=lambda m: m["cv_accuracy_std"])["name"]


def feature_importance(pipe: Pipeline) -> tuple[list[FeatureImportance], str]:
    """Top readable features (summing to 1) and a description of the method used."""
    model = pipe.named_steps["model"]
    names = pipe.named_steps["encode"].get_feature_names_out()
    if hasattr(model, "feature_importances_"):
        raw, method = model.feature_importances_, "model feature_importances_ (impurity-based)"
    else:
        raw = np.abs(model.coef_[0])
        method = "absolute logistic-regression coefficients (scaled features)"
    # Several encoded columns map to one readable name (Property_Area_Urban /
    # _Rural -> "Property Area"); add their importances together.
    grouped = pd.Series(raw, index=[friendly_name(n) for n in names]).groupby(level=0).sum()
    top = grouped.sort_values(ascending=False).head(TOP_FEATURES)
    top = top / top.sum()
    return [
        FeatureImportance(feature=str(f), importance=round(float(v), 4)) for f, v in top.items()
    ], method


# ----------------------------------------------------------------------- monotonicity --
BASE_PROFILES: Final[list[dict[str, Any]]] = [
    {
        "Gender": "Male",
        "Married": "Yes",
        "Dependents": "0",
        "Education": "Graduate",
        "Self_Employed": "No",
        "ApplicantIncome": 5000.0,
        "CoapplicantIncome": 1500.0,
        "LoanAmount": 130.0,
        "Loan_Amount_Term": 360.0,
        "Credit_History": 1.0,
        "Property_Area": "Semiurban",
    },
    {
        "Gender": "Female",
        "Married": "No",
        "Dependents": "2",
        "Education": "Not Graduate",
        "Self_Employed": "Yes",
        "ApplicantIncome": 2500.0,
        "CoapplicantIncome": 0.0,
        "LoanAmount": 200.0,
        "Loan_Amount_Term": 180.0,
        "Credit_History": 0.0,
        "Property_Area": "Rural",
    },
    {
        "Gender": "Male",
        "Married": "No",
        "Dependents": "3+",
        "Education": "Graduate",
        "Self_Employed": "No",
        "ApplicantIncome": 12000.0,
        "CoapplicantIncome": 4000.0,
        "LoanAmount": 60.0,
        "Loan_Amount_Term": 84.0,
        "Credit_History": 1.0,
        "Property_Area": "Urban",
    },
]
_SWEEP_POINTS: Final = 60
_INCOMES: Final = np.logspace(3, 7, _SWEEP_POINTS)  # ₹1,000 .. ₹1 crore per month
_LOANS_THOUSANDS: Final = np.logspace(1, 4, _SWEEP_POINTS)  # ₹10,000 .. ₹1 crore


def _sweeps() -> dict[str, tuple[dict[str, np.ndarray], int]]:
    """Sweep label -> (column overrides, required direction: +1 up, -1 down)."""
    return {
        "ApplicantIncome up": ({"ApplicantIncome": _INCOMES}, +1),
        "CoapplicantIncome up": ({"CoapplicantIncome": _INCOMES}, +1),
        "both incomes up": ({"ApplicantIncome": _INCOMES, "CoapplicantIncome": _INCOMES}, +1),
        "LoanAmount up": ({"LoanAmount": _LOANS_THOUSANDS}, -1),
    }


def check_monotonicity(pipe: Any, tol: float = 1e-9) -> list[SweepResult]:
    """Verify approval never falls as income rises nor rises as the loan grows.

    Each base profile is swept over income (applicant, co-applicant, both) and
    loan size.

    Returns:
        One :class:`SweepResult` per passed sweep.

    Raises:
        MonotonicityError: listing every failed sweep.
    """
    passed: list[SweepResult] = []
    failures: list[str] = []
    for index, base in enumerate(BASE_PROFILES, start=1):
        for label, (changes, direction) in _sweeps().items():
            rows = pd.DataFrame([base] * _SWEEP_POINTS)
            for column, values in changes.items():
                rows[column] = values
            p = pipe.predict_proba(rows)[:, 1]
            steps = np.diff(p) * direction
            if (steps < -tol).any():
                failures.append(
                    f"profile {index}: {label} (worst step {steps.min():+.4f}, "
                    f"P range {p.min():.3f}-{p.max():.3f})"
                )
            else:
                passed.append(SweepResult(index, label, float(p[0]), float(p[-1])))
    if failures:
        raise MonotonicityError("MONOTONICITY CHECK FAILED:\n  " + "\n  ".join(failures))
    return passed


def _score(name: str, y_true: pd.Series, y_pred: np.ndarray, cv_scores: np.ndarray) -> ModelMetrics:
    """Hold-out classification metrics plus CV accuracy statistics, rounded to 4 dp."""
    return ModelMetrics(
        name=name,
        accuracy=round(float(accuracy_score(y_true, y_pred)), 4),
        precision=round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        recall=round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        f1=round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        cv_accuracy_mean=round(float(cv_scores.mean()), 4),
        cv_accuracy_std=round(float(cv_scores.std()), 4),
    )
