"""Candidate model pipelines.

Every pipeline carries its own preprocessing (type coercion, imputation,
feature engineering, encoding, optional scaling) so the saved artefact accepts
the raw 11-column frame described in docs/API.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from loanwise.ml.features import (
    CATEGORICAL_COLS,
    MODEL_NUMERIC_COLS,
    MONOTONIC_DIRECTION,
    NUMERIC_COLS,
    add_engineered_features,
    coerce_raw_input,
)

RANDOM_STATE: Final = 42


@dataclass(frozen=True)
class Candidate:
    """A named pipeline and the small hyper-parameter grid searched for it."""

    name: str
    pipeline: Pipeline
    param_grid: dict[str, list[Any]]


def build_preprocessing_steps(*, scale_numeric: bool) -> list[tuple[str, Any]]:
    """Steps that turn the raw 11-column frame into a numeric matrix.

    Order: coerce types -> impute -> engineer features -> one-hot encode (+ scale).
    """
    imputer = ColumnTransformer(
        [
            ("cat", SimpleImputer(strategy="most_frequent"), CATEGORICAL_COLS),
            # Credit_History is 0/1, so "most frequent" (= 1) is safer than a median.
            ("credit", SimpleImputer(strategy="most_frequent"), ["Credit_History"]),
            (
                "num",
                SimpleImputer(strategy="median"),
                [c for c in NUMERIC_COLS if c != "Credit_History"],
            ),
        ],
        verbose_feature_names_out=False,
    )
    # The numeric block comes first so its column positions are fixed (needed for
    # the tree models' monotonic constraints). Only MODEL_NUMERIC_COLS reach the
    # model; raw incomes, loan amount and EMI are dropped here.
    encoder = ColumnTransformer(
        [
            ("num", StandardScaler() if scale_numeric else "passthrough", MODEL_NUMERIC_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return [
        ("clean", FunctionTransformer(coerce_raw_input)),
        ("impute", imputer),
        ("features", FunctionTransformer(add_engineered_features)),
        ("encode", encoder),
    ]


def build_pipeline(classifier: ClassifierMixin, *, scale_numeric: bool) -> Pipeline:
    """Append ``classifier`` to the preprocessing steps."""
    pipe = Pipeline(
        [*build_preprocessing_steps(scale_numeric=scale_numeric), ("model", classifier)]
    )
    # Keep DataFrames (with column names) flowing between steps so that
    # add_engineered_features can refer to columns by name.
    pipe[:-1].set_output(transform="pandas")
    return pipe


def monotonic_constraints(X: pd.DataFrame) -> list[int]:
    """Constraint vector for the tree models' ``monotonic_cst``.

    Order matches the encoder output: MODEL_NUMERIC_COLS, then the one-hot
    columns (unconstrained).
    """
    n_onehot = int(sum(X[c].dropna().astype(str).nunique() for c in CATEGORICAL_COLS))
    return [MONOTONIC_DIRECTION[c] for c in MODEL_NUMERIC_COLS] + [0] * n_onehot


def model_candidates(X: pd.DataFrame) -> list[Candidate]:
    """Logistic Regression, Decision Tree and Random Forest with their search grids."""
    constraints = monotonic_constraints(X)
    return [
        Candidate(
            "Logistic Regression",
            build_pipeline(LogisticRegression(max_iter=2000), scale_numeric=True),
            {"model__C": [0.01, 0.1, 1.0, 10.0]},
        ),
        Candidate(
            "Decision Tree",
            build_pipeline(
                DecisionTreeClassifier(random_state=RANDOM_STATE, monotonic_cst=constraints),
                scale_numeric=False,
            ),
            {"model__max_depth": [2, 3, 4, 6], "model__min_samples_leaf": [5, 10, 20]},
        ),
        Candidate(
            "Random Forest",
            build_pipeline(
                RandomForestClassifier(
                    n_estimators=300,
                    random_state=RANDOM_STATE,
                    monotonic_cst=constraints,
                    n_jobs=-1,
                ),
                scale_numeric=False,
            ),
            {"model__max_depth": [4, 6, 8], "model__min_samples_leaf": [3, 5, 10]},
        ),
    ]
