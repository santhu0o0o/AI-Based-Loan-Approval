"""Every plain-English string the domain layer can show to an applicant.

Templates use :meth:`str.format` placeholders. Wording is part of the product
("written for someone who has never applied for a loan") and is asserted by
tests, so change it deliberately.
"""

from __future__ import annotations

from typing import Final

from loanwise.domain import schemas as s

# ------------------------------------------------------------------------------ validation --
FIELD_LABELS: Final[dict[str, str]] = {
    s.GENDER: "gender",
    s.MARRIED: "marital status",
    s.DEPENDENTS: "number of dependents",
    s.EDUCATION: "education",
    s.SELF_EMPLOYED: "self-employed answer",
    s.APPLICANT_INCOME: "monthly income",
    s.COAPPLICANT_INCOME: "co-applicant's monthly income",
    s.LOAN_AMOUNT: "loan amount",
    s.LOAN_TERM: "loan length",
    s.CREDIT_HISTORY: "credit history",
    s.PROPERTY_AREA: "property area",
}

CHOICE_HELP: Final[dict[str, str]] = {
    s.GENDER: "Please choose Male or Female.",
    s.MARRIED: "Please choose Yes or No for 'Are you married?'.",
    s.DEPENDENTS: "Please choose how many people depend on you: 0, 1, 2 or 3+.",
    s.EDUCATION: "Please choose Graduate or Not Graduate.",
    s.SELF_EMPLOYED: "Please choose Yes or No for 'Do you work for yourself?'.",
    s.CREDIT_HISTORY: "Please choose Good (you paid past loans and cards on time) or Bad.",
    s.PROPERTY_AREA: "Please choose where the property is: Urban, Semiurban or Rural.",
}

NUMBER_HELP: Final[dict[str, str]] = {
    s.APPLICANT_INCOME: "Please type your monthly income using numbers only, like 25000.",
    s.COAPPLICANT_INCOME: (
        "Please type your co-applicant's monthly income using numbers only, "
        "like 15000. Type 0 if there is no co-applicant."
    ),
    s.LOAN_AMOUNT: (
        "Please type the loan amount you want in rupees using numbers only, like 500000."
    ),
    s.LOAN_TERM: (
        "Please choose how long you want to repay the loan: 12, 36, 60, 84, 120, "
        "180, 240, 300, 360 or 480 months."
    ),
}

MISSING_PREFIX: Final = "This answer is missing. "
NEGATIVE_PREFIX: Final = "This can't be a negative number. "
FORM_UNREADABLE: Final = (
    "We couldn't read your answers. Please fill in the form and press the button again."
)
DEPENDENTS_NOT_WHOLE: Final = "Please choose a whole number of dependents: 0, 1, 2 or 3+."
DEPENDENTS_TOO_MANY: Final = (
    "That is a lot of dependents. Please check the number and choose 0, 1, 2 or 3+."
)
INCOME_TOO_BIG: Final = (
    "That monthly income looks too big (more than {limit}). "
    "Please check you typed your MONTHLY income, not yearly, like 25000."
)
NO_INCOME: Final = (
    "At least one person must have some income. Please type "
    "your monthly income (or your co-applicant's), like 25000."
)
LOAN_TOO_SMALL: Final = (
    "The smallest loan we can check is {limit}. Please type the full amount in rupees, like 500000."
)
LOAN_TOO_BIG: Final = (
    "The biggest loan we can check is {limit} (1 crore). Please type a smaller amount, like 500000."
)
NOTE_AMOUNT_READ_AS: Final = 'We read your {label} "{raw}" as {amount}.'
NOTE_TERM_READ_AS: Final = 'We read your loan length "{raw}" as {months:.0f} months.'

# ------------------------------------------------------------------------------- sanitizer --
WARN_VERY_HIGH_INCOME: Final = (
    "Your total monthly income ({amount}) is very high. Please double-check "
    "you typed MONTHLY income, not yearly."
)

# ------------------------------------------------------------------------------ guardrails --
VERDICT_APPROVED: Final = "Likely Approved"
VERDICT_REJECTED: Final = "Likely Rejected"
HEADLINE_APPROVED: Final = "Great news! Your loan is likely to be approved."
HEADLINE_REJECTED: Final = "Sorry — your loan is likely to be rejected right now."
HEADLINE_UNAFFORDABLE: Final = "Sorry — this loan looks too big for your income right now."

REASON_EMI_UNAFFORDABLE: Final = (
    "The monthly payment would be about {emi}, which is {share}. Banks don't allow "
    "payments above about {limit:.0%} of income. Try a smaller loan or a longer repayment time."
)
EMI_SHARE_OF_INCOME: Final = "{ratio:.0%} of your total monthly income"
EMI_SHARE_ALL_INCOME: Final = "more than your whole monthly income"
REASON_LOAN_TOO_LARGE: Final = (
    "The loan ({loan}) is more than {years:.0f} years of "
    "your total income ({income} a month). Try asking for a smaller amount."
)
REASON_CREDIT_GOOD: Final = "Your credit history is good — this helps a lot."
REASON_CREDIT_BAD: Final = (
    "Your credit history is bad (past loans or cards not paid on time). "
    "This is the biggest reason loans get rejected."
)
REASON_EMI_EASY: Final = (
    "The monthly payment (about {emi}) is only {pct} of your income — easy to afford."
)
REASON_EMI_MANAGEABLE: Final = (
    "The monthly payment (about {emi}) is {pct} of your income — manageable, but not small."
)
REASON_EMI_STRETCH: Final = (
    "The monthly payment (about {emi}) is {pct} of your income — that is a big stretch."
)
REASON_LOAN_SENSIBLE: Final = (
    "The loan is about {years:.1f} years of your income — a sensible size."
)
REASON_LOAN_LARGE: Final = "The loan is about {years:.1f} years of your income — on the large side."
REASON_COAPPLICANT: Final = "Having a co-applicant with income makes the loan safer for the bank."
REASON_GRADUATE: Final = "Being a graduate helps a little."
REASON_ESTIMATE_ONLY: Final = (
    "This is an estimate from past loan data, not a bank's final decision."
)
