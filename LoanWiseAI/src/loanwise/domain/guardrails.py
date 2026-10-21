"""Guardrails: common-sense lending rules applied on top of the model.

The model was trained on 614 messy rows. Given valid-but-silly input (say a
₹1 crore loan on a ₹5,000 salary) it can still say "approved". These rules use
the applicant's **real** numbers to catch that.

All estimates use a standard amortised EMI at :data:`INTEREST_RATE_ANNUAL`
(9% a year): ``EMI = P·r·(1+r)^n / ((1+r)^n − 1)`` with ``r = 9% / 12``.

Rules, checked in this order:

R1  EMI above :data:`EMI_HARD_LIMIT` (65%) of total monthly income
    (applicant + co-applicant) -> force "Likely Rejected".
R2  Loan above :data:`LOAN_TO_INCOME_HARD` (60x) total monthly income
    (more than 5 years of all income) -> force "Likely Rejected".
R3  Bad credit history -> always reported as a negative reason. If the model
    still approves, confidence is capped at :data:`BAD_CREDIT_CONF_CAP` (0.65,
    at most "Medium") because lenders almost never approve these.
R4  EMI between 45% and 65% of income -> negative "stretch" reason (no override).

When R1 or R2 fires, ``guardrail_applied`` is true and the reported confidence
is ``max(model's rejection probability, OVERRIDE_CONFIDENCE)``: the rule is a
hard affordability fact, not a guess.

Guardrails never turn a model rejection into an approval; being conservative is
the safe failure mode for a loan-advice tool.

Confidence label (probability of the winning side): High >= 0.75,
Medium >= 0.60, otherwise Low.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, Literal, TypedDict

from loanwise.domain import messages as msg
from loanwise.domain import schemas as s
from loanwise.domain.formatting import format_inr

INTEREST_RATE_ANNUAL: Final = 0.09
EMI_HARD_LIMIT: Final = 0.65
EMI_STRETCH_LIMIT: Final = 0.45
EMI_COMFORT_LIMIT: Final = 0.30
LOAN_TO_INCOME_HARD: Final = 60.0
SENSIBLE_LOAN_YEARS: Final = 3.0
OVERRIDE_CONFIDENCE: Final = 0.90
BAD_CREDIT_CONF_CAP: Final = 0.65
APPROVAL_THRESHOLD: Final = 0.5
HIGH_CONFIDENCE: Final = 0.75
MEDIUM_CONFIDENCE: Final = 0.60
MAX_REASONS: Final = 5
MIN_REASONS: Final = 3

ReasonType = Literal["positive", "negative", "neutral"]


class Reason(TypedDict):
    """One plain-English explanation shown under the verdict."""

    type: ReasonType
    text: str


@dataclass
class Decision:
    """Final answer for one application (model output combined with guardrails)."""

    approved: bool
    verdict: str
    headline: str
    confidence: float
    confidence_label: str
    reasons: list[Reason] = field(default_factory=list)
    guardrail_applied: bool = False
    emi_estimate: float = 0.0
    approval_probability: float = 0.0  # model's raw P(approve), kept for history/debugging


@dataclass(frozen=True)
class Affordability:
    """Affordability figures derived from the applicant's real (unclamped) numbers."""

    income: float
    loan: float
    emi: float
    emi_ratio: float
    loan_multiple: float


def estimate_emi(principal: float, months: int, annual_rate: float = INTEREST_RATE_ANNUAL) -> float:
    """Return the standard amortised monthly instalment for a loan."""
    if months <= 0:
        return float(principal)
    rate = annual_rate / 12.0
    if rate == 0:
        return principal / months
    factor = (1 + rate) ** months
    return principal * rate * factor / (factor - 1)


def confidence_label(p_winning: float) -> str:
    """Map the winning side's probability to ``"High"``, ``"Medium"`` or ``"Low"``."""
    if p_winning >= HIGH_CONFIDENCE:
        return "High"
    if p_winning >= MEDIUM_CONFIDENCE:
        return "Medium"
    return "Low"


def assess_affordability(cleaned: dict[str, Any]) -> Affordability:
    """Compute EMI and income ratios from validated request fields."""
    income = float(cleaned[s.APPLICANT_INCOME]) + float(cleaned[s.COAPPLICANT_INCOME])
    loan = float(cleaned[s.LOAN_AMOUNT])
    emi = estimate_emi(loan, int(cleaned[s.LOAN_TERM]))
    return Affordability(
        income=income,
        loan=loan,
        emi=emi,
        emi_ratio=emi / income if income > 0 else float("inf"),
        loan_multiple=loan / income if income > 0 else float("inf"),
    )


def apply_guardrails(cleaned: dict[str, Any], p_approve: float) -> Decision:
    """Combine the model's approval probability with common-sense lending rules.

    Args:
        cleaned: validated request fields with the applicant's real values.
        p_approve: model probability of approval; clipped into ``[0, 1]``.
    """
    p_approve = min(max(float(p_approve), 0.0), 1.0)
    figures = assess_affordability(cleaned)
    good_credit = cleaned[s.CREDIT_HISTORY] == s.CREDIT_GOOD

    approved = p_approve >= APPROVAL_THRESHOLD
    confidence = p_approve if approved else 1 - p_approve
    overrides = _override_reasons(figures)
    guardrail_applied = bool(overrides)
    if guardrail_applied:
        approved = False
        confidence = max(1 - p_approve, OVERRIDE_CONFIDENCE)
    elif approved and not good_credit:
        confidence = min(confidence, BAD_CREDIT_CONF_CAP)  # R3

    verdict, headline = _verdict(approved=approved, guardrail_applied=guardrail_applied)
    confidence = round(float(confidence), 4)
    return Decision(
        approved=approved,
        verdict=verdict,
        headline=headline,
        confidence=confidence,
        confidence_label=confidence_label(confidence),
        reasons=_explain(cleaned, figures, overrides, good_credit=good_credit),
        guardrail_applied=guardrail_applied,
        emi_estimate=round(figures.emi, 2),
        approval_probability=round(p_approve, 4),
    )


# --------------------------------------------------------------------------------- helpers --
def _override_reasons(figures: Affordability) -> list[Reason]:
    """Reasons for the hard rules R1 and R2; non-empty means the loan is rejected."""
    reasons: list[Reason] = []
    if figures.emi_ratio > EMI_HARD_LIMIT:
        share = (
            msg.EMI_SHARE_OF_INCOME.format(ratio=figures.emi_ratio)
            if figures.emi_ratio < 1
            else msg.EMI_SHARE_ALL_INCOME
        )
        reasons.append(
            _reason(
                "negative",
                msg.REASON_EMI_UNAFFORDABLE.format(
                    emi=format_inr(figures.emi), share=share, limit=EMI_HARD_LIMIT
                ),
            )
        )
    if figures.loan_multiple > LOAN_TO_INCOME_HARD:
        reasons.append(
            _reason(
                "negative",
                msg.REASON_LOAN_TOO_LARGE.format(
                    loan=format_inr(figures.loan),
                    years=LOAN_TO_INCOME_HARD / 12,
                    income=format_inr(figures.income),
                ),
            )
        )
    return reasons


def _explain(
    cleaned: dict[str, Any], figures: Affordability, overrides: list[Reason], *, good_credit: bool
) -> list[Reason]:
    """Assemble 3-5 reasons (see MIN_REASONS / MAX_REASONS), most important first."""
    reasons = list(overrides)
    reasons.append(
        _reason("positive", msg.REASON_CREDIT_GOOD)
        if good_credit
        else _reason("negative", msg.REASON_CREDIT_BAD)
    )
    if figures.emi_ratio <= EMI_HARD_LIMIT:  # otherwise R1 already explained it
        reasons.append(_emi_reason(figures))
    if figures.loan_multiple <= LOAN_TO_INCOME_HARD:  # otherwise R2 already explained it
        reasons.append(_loan_size_reason(figures.loan_multiple / 12))
    if float(cleaned[s.COAPPLICANT_INCOME]) > 0:
        reasons.append(_reason("positive", msg.REASON_COAPPLICANT))
    if len(reasons) < MAX_REASONS and cleaned.get(s.EDUCATION) == s.GRADUATE:
        reasons.append(_reason("neutral", msg.REASON_GRADUATE))
    if len(reasons) < MIN_REASONS:
        reasons.append(_reason("neutral", msg.REASON_ESTIMATE_ONLY))
    return reasons[:MAX_REASONS]


def _emi_reason(figures: Affordability) -> Reason:
    """Describe how comfortable the monthly payment is (includes rule R4)."""
    emi, pct = format_inr(figures.emi), f"{figures.emi_ratio:.0%}"
    if figures.emi_ratio <= EMI_COMFORT_LIMIT:
        return _reason("positive", msg.REASON_EMI_EASY.format(emi=emi, pct=pct))
    if figures.emi_ratio <= EMI_STRETCH_LIMIT:
        return _reason("neutral", msg.REASON_EMI_MANAGEABLE.format(emi=emi, pct=pct))
    return _reason("negative", msg.REASON_EMI_STRETCH.format(emi=emi, pct=pct))


def _loan_size_reason(years: float) -> Reason:
    """Describe the loan size measured in years of total income."""
    if years <= SENSIBLE_LOAN_YEARS:
        return _reason("positive", msg.REASON_LOAN_SENSIBLE.format(years=years))
    return _reason("neutral", msg.REASON_LOAN_LARGE.format(years=years))


def _verdict(*, approved: bool, guardrail_applied: bool) -> tuple[str, str]:
    """Return the ``(verdict, headline)`` pair for the final decision."""
    if guardrail_applied:
        return msg.VERDICT_REJECTED, msg.HEADLINE_UNAFFORDABLE
    if approved:
        return msg.VERDICT_APPROVED, msg.HEADLINE_APPROVED
    return msg.VERDICT_REJECTED, msg.HEADLINE_REJECTED


def _reason(kind: ReasonType, text: str) -> Reason:
    """Build a :class:`Reason`."""
    return {"type": kind, "text": text}
