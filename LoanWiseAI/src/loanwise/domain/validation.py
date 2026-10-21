"""Layer 2: strict server-side validation of the loan form.

Philosophy ("built for someone who has never filled in a loan form"):

* Be **forgiving** about harmless formatting: extra spaces, any letter case,
  "₹", "Rs", commas, "25k", "2 lakh", "3+" / "4" children, "yes"/"no" for
  credit history, "360 months" / "30 years" for the term, and so on.
* Be **strict** about anything that changes meaning: missing answers, words
  where a number should be, negative numbers, NaN/Infinity, absurd sizes,
  true/false typed where a number should be, unknown choices, unsupported terms.
* Collect **every** problem at once (field -> plain-English message) so the
  applicant can fix the whole form in one go.
* Unknown extra fields are silently ignored.

Public API: :func:`validate_application` returning a :class:`ValidationResult`.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Final

from loanwise.domain import messages as msg
from loanwise.domain import schemas as s
from loanwise.domain.formatting import format_inr

_YES: Final = frozenset({"yes", "y", "true", "t", "1", "yeah", "yep", "ok"})
_NO: Final = frozenset({"no", "n", "false", "f", "0", "nope", "nah"})

# Lower-cased, whitespace-normalised answer -> canonical value.
CHOICE_SYNONYMS: Final[dict[str, dict[str, str]]] = {
    s.GENDER: {
        "male": "Male",
        "m": "Male",
        "man": "Male",
        "female": "Female",
        "f": "Female",
        "woman": "Female",
    },
    s.MARRIED: {
        **dict.fromkeys(_YES | {"married"}, "Yes"),
        **dict.fromkeys(_NO | {"single", "unmarried", "not married"}, "No"),
    },
    s.SELF_EMPLOYED: {
        **dict.fromkeys(_YES | {"self employed", "self-employed"}, "Yes"),
        **dict.fromkeys(_NO | {"salaried", "employed", "not self employed"}, "No"),
    },
    s.EDUCATION: {
        "graduate": "Graduate",
        "grad": "Graduate",
        "graduated": "Graduate",
        "yes": "Graduate",
        "not graduate": "Not Graduate",
        "not_graduate": "Not Graduate",
        "notgraduate": "Not Graduate",
        "not-graduate": "Not Graduate",
        "non graduate": "Not Graduate",
        "non-graduate": "Not Graduate",
        "nongraduate": "Not Graduate",
        "undergraduate": "Not Graduate",
        "no": "Not Graduate",
    },
    s.CREDIT_HISTORY: {
        **dict.fromkeys(_YES | {"good", "g", "clean", "1.0", "ok", "fine"}, s.CREDIT_GOOD),
        **dict.fromkeys(_NO | {"bad", "b", "poor", "0.0"}, s.CREDIT_BAD),
    },
    s.PROPERTY_AREA: {
        "urban": "Urban",
        "city": "Urban",
        "semiurban": "Semiurban",
        "semi urban": "Semiurban",
        "semi-urban": "Semiurban",
        "semi_urban": "Semiurban",
        "suburban": "Semiurban",
        "rural": "Rural",
        "village": "Rural",
    },
}

_DEPENDENTS_NONE: Final = frozenset({"none", "zero", "no"})
_DEPENDENTS_MANY: Final = frozenset(
    {"3+", "3 +", "3 or more", "more than 3", "3plus", "3 plus", "three+"}
)
_DEPENDENTS_WORDS: Final = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

_AMOUNT_MULTIPLIERS: Final = {
    "k": 1_000,
    "thousand": 1_000,
    "l": 100_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "lac": 100_000,
    "lacs": 100_000,
    "lk": 100_000,
    "cr": 10_000_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "m": 1_000_000,
    "million": 1_000_000,
    "mn": 1_000_000,
}
# Removed before parsing an amount (order matters: "rs." before "rs", "month" last).
_AMOUNT_NOISE: Final = (
    "₹",
    "inr",
    "rs.",
    "rs",
    "rupees",
    "rupee",
    "/-",
    "per month",
    "/month",
    "a month",
    "monthly",
    "month",
    "pm",
)
_NOT_A_NUMBER: Final = frozenset({"nan", "inf", "infinity", "+inf"})
_AMOUNT_RE: Final = re.compile(r"^([0-9]*\.?[0-9]+)\s*([a-z]*)$")
_TERM_RE: Final = re.compile(r"^([0-9]*\.?[0-9]+)\s*(months?|mos?|m|years?|yrs?|y)?$")
_SPACED_DIGITS_RE: Final = re.compile(r"(?<=\d) (?=\d)")


@dataclass
class ValidationResult:
    """Outcome of :func:`validate_application`.

    Attributes:
        cleaned: canonical values for every field that parsed successfully.
        errors: field name -> message for every field that did not.
        warnings: notes about harmless reinterpretations ("we read 25k as ₹25,000");
            emptied whenever there are errors.
    """

    cleaned: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when the form has no errors."""
        return not self.errors


class FieldError(ValueError):
    """Raised by field parsers; ``str(exc)`` is the exact message to show."""


# ------------------------------------------------------------------------------ public API --
def validate_application(payload: Any) -> ValidationResult:
    """Validate a decoded JSON payload. Never raises.

    Args:
        payload: anything ``json.loads`` can return; only a ``dict`` can be valid.
    """
    result = ValidationResult()
    if not isinstance(payload, dict):
        result.errors[s.FORM_ERROR_KEY] = msg.FORM_UNREADABLE
        return result

    notes = result.warnings
    for name in s.CHOICE_FIELDS:
        _record(result, name, partial(_parse_choice, name, payload.get(name)))
    _record(result, s.DEPENDENTS, partial(_parse_dependents, payload.get(s.DEPENDENTS)))
    _validate_incomes(result, payload, notes)
    _record(result, s.LOAN_AMOUNT, partial(_parse_loan_amount, payload.get(s.LOAN_AMOUNT), notes))
    _record(result, s.LOAN_TERM, partial(_parse_term, payload.get(s.LOAN_TERM), notes))

    if result.errors:
        result.warnings = []  # notes are only useful once the form is accepted
    return result


def parse_number(value: Any, name: str, notes: list[str] | None = None) -> float:
    """Turn a user-typed amount into a non-negative float.

    Accepts ``25000``, ``25000.5``, ``"25,000"``, ``"₹ 25000"``, ``"Rs. 25000"``,
    ``"INR 25000"``, ``"25k"``, ``"2.5 lakh"``, ``"1 crore"``. When a word
    multiplier is used, a note explaining the reading is appended to ``notes``.

    Raises:
        FieldError: for booleans, words, negatives, NaN/Infinity, lists or objects.
    """
    help_msg = msg.NUMBER_HELP[name]
    if value is None:
        raise FieldError(_missing(name))
    if isinstance(value, bool):
        raise FieldError(help_msg)
    if isinstance(value, (int, float)):
        num = float(value)
    elif isinstance(value, str):
        num = _parse_amount_text(value, name, notes)
    else:
        raise FieldError(help_msg)

    if not math.isfinite(num):
        raise FieldError(help_msg)
    if num < 0:
        raise FieldError(msg.NEGATIVE_PREFIX + help_msg)
    return num


# --------------------------------------------------------------------------------- helpers --
def _record(result: ValidationResult, name: str, parse: Callable[[], Any]) -> None:
    """Store ``parse()`` under ``name`` in cleaned, or its error message in errors."""
    try:
        result.cleaned[name] = parse()
    except FieldError as exc:
        result.errors[name] = str(exc)


def _missing(name: str) -> str:
    """Message for a required answer that was left blank."""
    return msg.MISSING_PREFIX + msg.NUMBER_HELP.get(name, msg.CHOICE_HELP.get(name, ""))


def _normalise_text(value: Any, name: str) -> str:
    """Normalise a choice answer to lower-case, single-spaced text."""
    if value is None:
        raise FieldError(_missing(name))
    if isinstance(value, bool):
        return "yes" if value else "no"  # only meaningful for yes/no style questions
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise FieldError(msg.CHOICE_HELP[name])
        return str(int(value)) if float(value).is_integer() else str(value)
    if not isinstance(value, str):
        raise FieldError(msg.CHOICE_HELP[name])
    text = " ".join(value.strip().lower().split())
    if not text:
        raise FieldError(_missing(name))
    if len(text) > s.MAX_TEXT_LEN:
        raise FieldError(msg.CHOICE_HELP[name])
    return text


def _parse_choice(name: str, value: Any) -> str:
    """Map a choice answer (or a known synonym) onto its canonical value."""
    text = _normalise_text(value, name)
    canonical = CHOICE_SYNONYMS[name].get(text)
    if canonical is None:
        raise FieldError(msg.CHOICE_HELP[name])
    return canonical


def _parse_dependents(value: Any) -> str:
    """Parse the number of dependents into ``"0"``, ``"1"``, ``"2"`` or ``"3+"``."""
    if isinstance(value, bool):
        raise FieldError(msg.CHOICE_HELP[s.DEPENDENTS])
    text = _normalise_text(value, s.DEPENDENTS)
    if text in _DEPENDENTS_NONE:
        return "0"
    if text in _DEPENDENTS_MANY:
        return "3+"
    count = _DEPENDENTS_WORDS.get(text)
    if count is None:
        count = _parse_whole_count(text)
    if count > s.MAX_DEPENDENTS:
        raise FieldError(msg.DEPENDENTS_TOO_MANY)
    return "3+" if count >= s.DEPENDENTS_CAP else str(count)


def _parse_whole_count(text: str) -> int:
    """Parse a numeric dependents answer that must be a non-negative whole number."""
    try:
        num = float(text)
    except ValueError:
        raise FieldError(msg.CHOICE_HELP[s.DEPENDENTS]) from None
    if not math.isfinite(num) or num < 0 or not num.is_integer():
        raise FieldError(msg.DEPENDENTS_NOT_WHOLE)
    return int(num)


def _parse_amount_text(value: str, name: str, notes: list[str] | None) -> float:
    """Parse a typed amount such as ``"₹ 2.5 lakh"`` (sign checks included)."""
    help_msg = msg.NUMBER_HELP[name]
    text = value.strip().lower()
    if not text:
        raise FieldError(_missing(name))
    if len(text) > s.MAX_TEXT_LEN:
        raise FieldError(help_msg)
    if text.startswith(("-", "−")):
        raise FieldError(msg.NEGATIVE_PREFIX + help_msg)
    for token in _AMOUNT_NOISE:
        text = text.replace(token, " ")
    text = text.replace(",", "").replace("_", "").replace("'", "")
    text = _SPACED_DIGITS_RE.sub("", " ".join(text.split()))  # "25 000" -> "25000"
    if text in _NOT_A_NUMBER:
        raise FieldError(help_msg)
    match = _AMOUNT_RE.match(text)
    if not match:
        raise FieldError(help_msg)
    num = float(match.group(1))
    suffix = match.group(2)
    if suffix:
        if suffix not in _AMOUNT_MULTIPLIERS:
            raise FieldError(help_msg)
        num *= _AMOUNT_MULTIPLIERS[suffix]
        if notes is not None:
            notes.append(
                msg.NOTE_AMOUNT_READ_AS.format(
                    label=msg.FIELD_LABELS[name], raw=value.strip(), amount=format_inr(num)
                )
            )
    return num


def _validate_incomes(result: ValidationResult, payload: dict[str, Any], notes: list[str]) -> None:
    """Validate both incomes, then require that at least one of them is positive."""
    for name in s.INCOME_FIELDS:
        raw = payload.get(name)
        if name == s.COAPPLICANT_INCOME and _is_blank(raw):
            result.cleaned[name] = 0.0  # no co-applicant is the common case
            continue
        _record(result, name, partial(_parse_income, raw, name, notes))

    cleaned = result.cleaned
    if (
        s.APPLICANT_INCOME in cleaned
        and s.COAPPLICANT_INCOME in cleaned
        and cleaned[s.APPLICANT_INCOME] + cleaned[s.COAPPLICANT_INCOME] <= 0
    ):
        result.errors[s.APPLICANT_INCOME] = msg.NO_INCOME


def _is_blank(value: Any) -> bool:
    """True for ``None`` or a whitespace-only string."""
    return value is None or (isinstance(value, str) and not value.strip())


def _parse_income(value: Any, name: str, notes: list[str]) -> float:
    """Parse a monthly income and enforce the upper limit."""
    num = parse_number(value, name, notes)
    if num > s.INCOME_MAX:
        raise FieldError(msg.INCOME_TOO_BIG.format(limit=format_inr(s.INCOME_MAX)))
    return round(num, 2)


def _parse_loan_amount(value: Any, notes: list[str]) -> float:
    """Parse the full-rupee loan amount and enforce its range."""
    num = parse_number(value, s.LOAN_AMOUNT, notes)
    if num < s.LOAN_MIN:
        raise FieldError(msg.LOAN_TOO_SMALL.format(limit=format_inr(s.LOAN_MIN)))
    if num > s.LOAN_MAX:
        raise FieldError(msg.LOAN_TOO_BIG.format(limit=format_inr(s.LOAN_MAX)))
    return round(num, 2)


def _parse_term(value: Any, notes: list[str]) -> int:
    """Parse the repayment period (months, or years when stated) into an allowed term."""
    help_msg = msg.NUMBER_HELP[s.LOAN_TERM]
    if value is None:
        raise FieldError(_missing(s.LOAN_TERM))
    if isinstance(value, bool):
        raise FieldError(help_msg)
    if isinstance(value, str):
        months = _parse_term_text(value, notes)
    elif isinstance(value, (int, float)):
        months = float(value)
    else:
        raise FieldError(help_msg)
    if not math.isfinite(months) or months <= 0:
        raise FieldError(help_msg)
    if not months.is_integer() or int(months) not in s.ALLOWED_LOAN_TERMS:
        raise FieldError(help_msg)
    return int(months)


def _parse_term_text(value: str, notes: list[str]) -> float:
    """Parse ``"360"``, ``"360 months"`` or ``"30 years"`` into a number of months."""
    text = " ".join(value.strip().lower().split())
    if not text:
        raise FieldError(_missing(s.LOAN_TERM))
    match = _TERM_RE.match(text)
    if not match:
        raise FieldError(msg.NUMBER_HELP[s.LOAN_TERM])
    months = float(match.group(1))
    if (match.group(2) or "").startswith("y"):
        months *= 12
        notes.append(msg.NOTE_TERM_READ_AS.format(raw=value.strip(), months=months))
    return months
