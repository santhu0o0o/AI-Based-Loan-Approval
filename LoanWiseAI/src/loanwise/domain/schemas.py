"""Single source of truth for field names, allowed values and numeric limits.

Two vocabularies exist and both are defined here:

* **Request fields** (snake_case) are what the HTTP API accepts (docs/API.md).
* **Model columns** are the dataset column names the trained pipeline expects.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------- request fields --
GENDER: Final = "gender"
MARRIED: Final = "married"
DEPENDENTS: Final = "dependents"
EDUCATION: Final = "education"
SELF_EMPLOYED: Final = "self_employed"
APPLICANT_INCOME: Final = "applicant_income"
COAPPLICANT_INCOME: Final = "coapplicant_income"
LOAN_AMOUNT: Final = "loan_amount"
LOAN_TERM: Final = "loan_term"
CREDIT_HISTORY: Final = "credit_history"
PROPERTY_AREA: Final = "property_area"

REQUEST_FIELDS: Final[tuple[str, ...]] = (
    GENDER,
    MARRIED,
    DEPENDENTS,
    EDUCATION,
    SELF_EMPLOYED,
    APPLICANT_INCOME,
    COAPPLICANT_INCOME,
    LOAN_AMOUNT,
    LOAN_TERM,
    CREDIT_HISTORY,
    PROPERTY_AREA,
)

# Fields answered by picking one option from a fixed list (dependents has its own parser).
CHOICE_FIELDS: Final[tuple[str, ...]] = (
    GENDER,
    MARRIED,
    EDUCATION,
    SELF_EMPLOYED,
    CREDIT_HISTORY,
    PROPERTY_AREA,
)
INCOME_FIELDS: Final[tuple[str, ...]] = (APPLICANT_INCOME, COAPPLICANT_INCOME)

# Pseudo-field used when the payload as a whole is unusable.
FORM_ERROR_KEY: Final = "_form"

# ----------------------------------------------------------------------- canonical values --
GENDER_VALUES: Final = ("Male", "Female")
YES_NO_VALUES: Final = ("Yes", "No")
DEPENDENTS_VALUES: Final = ("0", "1", "2", "3+")
EDUCATION_VALUES: Final = ("Graduate", "Not Graduate")
PROPERTY_AREA_VALUES: Final = ("Urban", "Semiurban", "Rural")
CREDIT_GOOD: Final = "good"
CREDIT_BAD: Final = "bad"
GRADUATE: Final = "Graduate"

# --------------------------------------------------------------------------------- limits --
ALLOWED_LOAN_TERMS: Final[tuple[int, ...]] = (12, 36, 60, 84, 120, 180, 240, 300, 360, 480)
INCOME_MAX: Final = 10_000_000  # monthly ₹
LOAN_MIN: Final = 1_000  # full ₹
LOAN_MAX: Final = 10_000_000  # full ₹
MAX_TEXT_LEN: Final = 60  # nobody needs more characters than this for one answer
MAX_DEPENDENTS: Final = 30
DEPENDENTS_CAP: Final = 3  # 3 or more people collapse into "3+"

# ---------------------------------------------------------------------------- model columns --
CATEGORICAL_COLUMNS: Final[tuple[str, ...]] = (
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "Property_Area",
)
NUMERIC_COLUMNS: Final[tuple[str, ...]] = (
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
)
# Column order of the DataFrame handed to the model (the API contract order).
MODEL_COLUMNS: Final[tuple[str, ...]] = (
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Property_Area",
)
LOAN_ID_COLUMN: Final = "Loan_ID"
TARGET_COLUMN: Final = "Loan_Status"
TARGET_APPROVED: Final = "Y"

# The dataset stores LoanAmount in thousands of ₹; the API takes full rupees.
LOAN_AMOUNT_UNIT: Final = 1000.0
