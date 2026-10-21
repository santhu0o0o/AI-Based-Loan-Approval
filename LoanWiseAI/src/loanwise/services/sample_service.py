"""Example applications for the "Fill example" button.

Rows come from the unlabelled demo CSV (``data/raw/test.csv``). Blank cells are
filled with typical values so that every sample passes validation.
"""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import pandas as pd

from loanwise.domain import schemas as s

log = logging.getLogger(__name__)

# Typical values (dataset units) used when a demo row has a blank cell.
_DEFAULTS: Final[dict[str, Any]] = {
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": "0",
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome": 3800,
    "CoapplicantIncome": 0,
    "LoanAmount": 128,
    "Loan_Amount_Term": 360,
    "Credit_History": 1.0,
    "Property_Area": "Urban",
}


class SampleUnavailableError(Exception):
    """The demo data could not be read or converted."""


@dataclass(frozen=True)
class SampleApplication:
    """One demo application in request-field format, plus its source ``Loan_ID``."""

    fields: dict[str, Any]
    loan_id: str | None


class SampleService:
    """Picks a random demo row and converts it to request fields."""

    def __init__(self, csv_path: Path) -> None:
        """Use ``csv_path`` (read on every call so edits are picked up immediately)."""
        self.csv_path = csv_path

    def random_application(self) -> SampleApplication:
        """Return a random demo application.

        Raises:
            SampleUnavailableError: if the CSV is missing, empty or malformed.
        """
        try:
            frame = pd.read_csv(self.csv_path, dtype={"Dependents": str})
            row = frame.iloc[random.randrange(len(frame))].to_dict()  # noqa: S311 - not security
            fields = row_to_application(row)
        except Exception as exc:
            log.exception("Could not build sample from %s", self.csv_path)
            raise SampleUnavailableError from exc
        loan_id = row.get(s.LOAN_ID_COLUMN)
        return SampleApplication(fields=fields, loan_id=None if _is_nan(loan_id) else str(loan_id))


def row_to_application(row: dict[str, Any]) -> dict[str, Any]:
    """Map a dataset-style row to API request fields, filling blanks sensibly."""

    def pick(column: str) -> Any:
        value = row.get(column)
        if _is_nan(value) or (isinstance(value, str) and not value.strip()):
            return _DEFAULTS[column]
        return value

    term = float(pick("Loan_Amount_Term"))
    nearest_term = min(s.ALLOWED_LOAN_TERMS, key=lambda allowed: abs(allowed - term))
    applicant = float(pick("ApplicantIncome"))
    coapplicant = float(pick("CoapplicantIncome"))
    if applicant + coapplicant <= 0:
        applicant = float(_DEFAULTS["ApplicantIncome"])
    dependents = str(pick("Dependents")).strip()
    if dependents not in s.DEPENDENTS_VALUES:
        dependents = _DEFAULTS["Dependents"]
    loan_thousands = max(float(pick("LoanAmount")), 1)
    return {
        s.GENDER: pick("Gender"),
        s.MARRIED: pick("Married"),
        s.DEPENDENTS: dependents,
        s.EDUCATION: pick("Education"),
        s.SELF_EMPLOYED: pick("Self_Employed"),
        s.APPLICANT_INCOME: round(applicant),
        s.COAPPLICANT_INCOME: round(coapplicant),
        s.LOAN_AMOUNT: round(loan_thousands * s.LOAN_AMOUNT_UNIT),
        s.LOAN_TERM: int(nearest_term),
        s.CREDIT_HISTORY: s.CREDIT_BAD if float(pick("Credit_History")) == 0.0 else s.CREDIT_GOOD,
        s.PROPERTY_AREA: pick("Property_Area"),
    }


def _is_nan(value: Any) -> bool:
    """True for ``None`` and float NaN (including numpy floats)."""
    return value is None or (isinstance(value, float) and math.isnan(value))
