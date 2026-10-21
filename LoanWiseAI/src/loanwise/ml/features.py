"""Feature engineering used inside the saved scikit-learn pipeline.

The pickled model references these functions by import path
(``loanwise.ml.features.coerce_raw_input`` and friends), so this module must
stay importable under that name wherever the model is loaded, and it must
only contain plain module-level functions (no lambdas) so the pipeline pickles.

Income and loan size reach the model **only** through the affordability ratio
EMI / total income. On this small dataset raw incomes picked up
counter-intuitive signs ("more income -> lower approval") that explode for very
large incomes. Using the ratio guarantees:

* more income -> lower ratio -> never lower approval;
* bigger loan -> higher ratio -> never higher approval.

Both directions are enforced by monotonic constraints and verified by
:func:`loanwise.ml.evaluation.check_monotonicity` before a model is saved.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from loanwise.domain.schemas import CATEGORICAL_COLUMNS, LOAN_AMOUNT_UNIT, NUMERIC_COLUMNS

CATEGORICAL_COLS: Final[list[str]] = list(CATEGORICAL_COLUMNS)
NUMERIC_COLS: Final[list[str]] = list(NUMERIC_COLUMNS)
RAW_COLS: Final[list[str]] = CATEGORICAL_COLS + NUMERIC_COLS

# Numeric columns the classifier actually sees (after feature engineering).
MODEL_NUMERIC_COLS: Final[list[str]] = [
    "Credit_History",
    "Loan_Amount_Term",
    "Log_EMI_Income_Ratio",
]

# Required direction of effect on approval: +1 increasing, -1 decreasing, 0 unconstrained.
MONOTONIC_DIRECTION: Final[dict[str, int]] = {
    "Credit_History": 1,
    "Loan_Amount_Term": 0,
    "Log_EMI_Income_Ratio": -1,
}

# The ratio is clipped to this range before the log so extreme inputs stay sane.
EMI_RATIO_CLIP: Final[tuple[float, float]] = (0.0, 10.0)

# Human-readable names used when reporting feature importance.
FRIENDLY_NAMES: Final[dict[str, str]] = {
    "Gender": "Gender",
    "Married": "Marital Status",
    "Dependents": "Number of Dependents",
    "Education": "Education",
    "Self_Employed": "Self Employed",
    "Property_Area": "Property Area",
    "ApplicantIncome": "Applicant Income",
    "CoapplicantIncome": "Co-applicant Income",
    "LoanAmount": "Loan Amount",
    "Loan_Amount_Term": "Loan Term",
    "Credit_History": "Credit History",
    "TotalIncome": "Total Income",
    "EMI": "Monthly Instalment (EMI)",
    "EMI_Income_Ratio": "EMI-to-Income Ratio",
    "Log_EMI_Income_Ratio": "EMI-to-Income Ratio",
}
_MISSING_TOKENS: Final = ["", "nan", "None"]


def coerce_raw_input(X: pd.DataFrame) -> pd.DataFrame:
    """Pipeline step 0: make any incoming frame look like the training data.

    * keeps exactly the 11 contract columns (missing ones become NaN, extras dropped);
    * categoricals become stripped Python strings or NaN (``0`` -> ``"0"``);
    * numerics become float (non-numeric junk becomes NaN and is imputed later).
    """
    X = pd.DataFrame(X).reindex(columns=RAW_COLS)
    out = pd.DataFrame(index=X.index)
    for col in CATEGORICAL_COLS:
        values = X[col].astype(object)
        out[col] = values.where(values.isna(), values.astype(str).str.strip()).astype(object)
        out.loc[out[col].isin(_MISSING_TOKENS), col] = np.nan
    for col in NUMERIC_COLS:
        out[col] = pd.to_numeric(X[col], errors="coerce").astype(float)
    return out


def add_engineered_features(X: pd.DataFrame) -> pd.DataFrame:
    """Pipeline step 2 (after imputation, so no NaN): add affordability columns.

    ``LoanAmount`` is in thousands of ₹ and incomes are monthly ₹. The EMI here
    is a simple interest-free instalment; it only needs to be monotonic.
    """
    X = X.copy()
    income = X["ApplicantIncome"].astype(float) + X["CoapplicantIncome"].astype(float)
    loan_rupees = X["LoanAmount"].astype(float) * LOAN_AMOUNT_UNIT
    term = X["Loan_Amount_Term"].astype(float).clip(lower=1.0)  # avoid division by zero
    safe_income = income.clip(lower=1.0)

    X["TotalIncome"] = income
    X["EMI"] = loan_rupees / term
    X["EMI_Income_Ratio"] = X["EMI"] / safe_income
    X["Log_EMI_Income_Ratio"] = np.log1p(X["EMI_Income_Ratio"].clip(*EMI_RATIO_CLIP))
    return X


def friendly_name(feature_name: str) -> str:
    """Map a transformed feature name (e.g. ``Property_Area_Urban``) to a readable label."""
    for raw in sorted(FRIENDLY_NAMES, key=len, reverse=True):
        if feature_name == raw or feature_name.startswith(raw + "_"):
            return FRIENDLY_NAMES[raw]
    return feature_name
