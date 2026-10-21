"""Layer 3: turn validated answers into the exact DataFrame the model expects.

* Renames request fields to dataset column names (see docs/API.md).
* Converts units: ``loan_amount`` in full ₹ -> ``LoanAmount`` in thousands of ₹;
  ``credit_history`` ``"good"``/``"bad"`` -> ``1.0``/``0.0``.
* Passes real amounts through unchanged. The model only sees income and loan
  size via a capped EMI-to-income ratio and is verified to be monotonic at
  training time, so clamping here would only distort that ratio.
* Adds a plain-English warning when the total income looks like a typo
  (yearly income entered as monthly, or an extra zero).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

import pandas as pd

from loanwise.domain import messages as msg
from loanwise.domain import schemas as s
from loanwise.domain.formatting import format_inr

# Above this total monthly income we ask the applicant to double-check.
SUSPICIOUS_MONTHLY_INCOME: Final = 500_000.0


@dataclass
class SanitizedInput:
    """A one-row model input frame plus any warnings raised while building it."""

    frame: pd.DataFrame
    warnings: list[str] = field(default_factory=list)


def to_model_frame(cleaned: dict[str, Any]) -> SanitizedInput:
    """Build the model input from :attr:`ValidationResult.cleaned` (already validated)."""
    applicant_income = float(cleaned[s.APPLICANT_INCOME])
    coapplicant_income = float(cleaned[s.COAPPLICANT_INCOME])
    row: dict[str, str | float] = {
        "Gender": cleaned[s.GENDER],
        "Married": cleaned[s.MARRIED],
        "Dependents": cleaned[s.DEPENDENTS],
        "Education": cleaned[s.EDUCATION],
        "Self_Employed": cleaned[s.SELF_EMPLOYED],
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": float(cleaned[s.LOAN_AMOUNT]) / s.LOAN_AMOUNT_UNIT,
        "Loan_Amount_Term": float(cleaned[s.LOAN_TERM]),
        "Credit_History": 1.0 if cleaned[s.CREDIT_HISTORY] == s.CREDIT_GOOD else 0.0,
        "Property_Area": cleaned[s.PROPERTY_AREA],
    }
    warnings: list[str] = []
    total_income = applicant_income + coapplicant_income
    if total_income > SUSPICIOUS_MONTHLY_INCOME:
        warnings.append(msg.WARN_VERY_HIGH_INCOME.format(amount=format_inr(total_income)))
    frame = pd.DataFrame([row], columns=list(s.MODEL_COLUMNS))
    return SanitizedInput(frame=frame, warnings=warnings)
