"""Smoke-test a saved model in a fresh interpreter, exactly as the API would load it.

Run by :mod:`loanwise.ml.train` as
``python -m loanwise.ml.sanity <model.pkl> <sample.csv>``; exits non-zero if
the model cannot be loaded or scored.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from loanwise.domain.schemas import LOAN_ID_COLUMN, MODEL_COLUMNS

_GOOD_PROFILE: dict[str, object] = {
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": "0",
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome": 8000.0,
    "CoapplicantIncome": 2000.0,
    "LoanAmount": 120.0,
    "Loan_Amount_Term": 360.0,
    "Credit_History": 1.0,
    "Property_Area": "Semiurban",
}
_DEMO_ROWS = 5


def probe_frame() -> pd.DataFrame:
    """Hand-made rows covering a good profile, bad credit, all-missing and huge income."""
    return pd.DataFrame(
        [
            _GOOD_PROFILE,
            {**_GOOD_PROFILE, "Credit_History": 0.0},
            dict.fromkeys(MODEL_COLUMNS, np.nan),
            {**_GOOD_PROFILE, "ApplicantIncome": 9_000_000.0, "LoanAmount": 100.0},
        ],
        index=["good profile", "bad credit", "all NaN", "90 lakh income"],
    )


def run(model_path: Path, sample_csv: Path) -> list[str]:
    """Load the model and return report lines with P(approve) for probes and demo rows."""
    pipe = joblib.load(model_path)
    lines = [f"Classes: {list(pipe.classes_)} -> predict_proba[:, 1] = P(approved)"]
    probes = probe_frame()
    for label, p in zip(probes.index, pipe.predict_proba(probes)[:, 1], strict=True):
        lines.append(f"  {label:<14} P(approve) = {p:.3f}")
    demo = pd.read_csv(sample_csv).head(_DEMO_ROWS)
    probs = pipe.predict_proba(demo.drop(columns=[LOAN_ID_COLUMN]))[:, 1]
    for loan_id, p in zip(demo[LOAN_ID_COLUMN], probs, strict=True):
        lines.append(f"  {loan_id:<14} P(approve) = {p:.3f}")
    return lines


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point: ``python -m loanwise.ml.sanity MODEL_PATH SAMPLE_CSV``."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        raise SystemExit("usage: python -m loanwise.ml.sanity MODEL_PATH SAMPLE_CSV")
    print("\n".join(run(Path(args[0]), Path(args[1]))))


if __name__ == "__main__":
    main()
