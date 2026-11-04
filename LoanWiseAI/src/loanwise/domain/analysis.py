"""Domain analysis: detailed explanations, financial metrics, and improvement recommendations.

Generates deep plain-English explanations for both approved and rejected loans,
and provides concrete, actionable levers applicants can adjust to turn a
rejection into an approval.
"""

from __future__ import annotations

import math
from typing import Any, Final, TypedDict

from loanwise.domain import schemas as s
from loanwise.domain.formatting import format_inr
from loanwise.domain.guardrails import (
    Affordability,
    EMI_COMFORT_LIMIT,
    EMI_HARD_LIMIT,
    EMI_STRETCH_LIMIT,
    INTEREST_RATE_ANNUAL,
    LOAN_TO_INCOME_HARD,
    SENSIBLE_LOAN_YEARS,
    estimate_emi,
)

TARGET_SAFE_DTI: Final[float] = 0.40  # 40% debt-to-income is standard conservative bank target


class ImprovementSuggestion(TypedDict):
    """Actionable advice for the applicant to improve approval chances."""

    category: str
    title: str
    description: str
    action: str


class FinancialMetrics(TypedDict):
    """Comprehensive financial metrics for display and reporting."""

    applicant_income: float
    coapplicant_income: float
    total_income: float
    loan_amount: float
    loan_term_months: int
    loan_term_years: float
    estimated_emi: float
    emi_to_income_ratio: float
    emi_to_income_pct: str
    loan_to_income_multiple: float
    loan_to_income_years: float
    affordability_band: str
    max_safe_loan_amount: float
    credit_status: str


def compute_financial_metrics(cleaned: dict[str, Any], figures: Affordability) -> FinancialMetrics:
    """Compute detailed financial ratios and affordability bands."""
    applicant_inc = float(cleaned.get(s.APPLICANT_INCOME, 0))
    coapplicant_inc = float(cleaned.get(s.COAPPLICANT_INCOME, 0))
    term_months = int(cleaned.get(s.LOAN_TERM, 240))
    term_years = round(term_months / 12.0, 1)

    if figures.emi_ratio <= EMI_COMFORT_LIMIT:
        band = "Comfortable"
    elif figures.emi_ratio <= EMI_STRETCH_LIMIT:
        band = "Manageable"
    elif figures.emi_ratio <= EMI_HARD_LIMIT:
        band = "Stretched"
    else:
        band = "Critical / Unaffordable"

    # Calculate maximum recommended loan at TARGET_SAFE_DTI (40% of income)
    max_safe_loan = calculate_max_loan(figures.income, term_months, target_dti=TARGET_SAFE_DTI)
    good_credit = cleaned.get(s.CREDIT_HISTORY) == s.CREDIT_GOOD

    return FinancialMetrics(
        applicant_income=applicant_inc,
        coapplicant_income=coapplicant_inc,
        total_income=figures.income,
        loan_amount=figures.loan,
        loan_term_months=term_months,
        loan_term_years=term_years,
        estimated_emi=round(figures.emi, 2),
        emi_to_income_ratio=round(figures.emi_ratio, 4),
        emi_to_income_pct=f"{figures.emi_ratio:.1%}",
        loan_to_income_multiple=round(figures.loan_multiple, 2),
        loan_to_income_years=round(figures.loan_multiple / 12.0, 2),
        affordability_band=band,
        max_safe_loan_amount=round(max_safe_loan, 2),
        credit_status="Good (Clean history)" if good_credit else "Unfavorable (Past delays/defaults)",
    )


def calculate_max_loan(
    monthly_income: float,
    months: int,
    annual_rate: float = INTEREST_RATE_ANNUAL,
    target_dti: float = TARGET_SAFE_DTI,
) -> float:
    """Calculate the principal loan amount for a given monthly income and target DTI."""
    if monthly_income <= 0 or months <= 0:
        return 0.0
    rate = annual_rate / 12.0
    if rate == 0:
        return (target_dti * monthly_income) * months
    target_monthly_payment = target_dti * monthly_income
    factor = (1 + rate) ** months
    if factor <= 1:
        return 0.0
    return target_monthly_payment * (factor - 1) / (rate * factor)


def generate_detailed_explanation(
    cleaned: dict[str, Any],
    figures: Affordability,
    *,
    approved: bool,
    guardrail_applied: bool,
    confidence: float,
    confidence_label: str,
    p_approve: float,
) -> str:
    """Produce a thorough plain-English narrative analyzing the loan application."""
    good_credit = cleaned.get(s.CREDIT_HISTORY) == s.CREDIT_GOOD
    term_years = int(cleaned.get(s.LOAN_TERM, 240)) // 12
    emi_str = format_inr(figures.emi)
    loan_str = format_inr(figures.loan)
    income_str = format_inr(figures.income)
    ratio_pct = f"{figures.emi_ratio:.1%}"
    loan_years = f"{figures.loan_multiple / 12.0:.1f}"

    lines: list[str] = []

    # 1. Executive Summary
    if approved:
        lines.append(
            f"Your home loan application of {loan_str} over {term_years} years is assessed as "
            f"LIKELY APPROVED with {confidence_label} confidence ({confidence:.1%}). "
            "Our automated underwriting model and banking affordability guardrails indicate that your financial "
            "profile presents a manageable risk profile for retail mortgage lenders."
        )
    else:
        if guardrail_applied:
            lines.append(
                f"Your home loan application of {loan_str} over {term_years} years is assessed as "
                f"LIKELY REJECTED. Although statistical pattern models may look at individual factors, "
                "our banking prudence guardrails flagged this request because the borrowing burden exceeds "
                "standard debt-service safety thresholds."
            )
        else:
            lines.append(
                f"Your home loan application of {loan_str} over {term_years} years is assessed as "
                f"LIKELY REJECTED with {confidence_label} confidence ({confidence:.1%}). "
                "Based on patterns from historical loan applications and lender underwriting standards, "
                "key risk factors in your application currently lower your approval probability."
            )

    # 2. Affordability & Cash Flow Assessment
    lines.append(
        f"Affordability & Debt Service: At a standard benchmark interest rate of 9.0% per annum, "
        f"your estimated monthly installment (EMI) would be approximately {emi_str}. "
        f"Against your total household monthly income of {income_str}, this monthly obligation accounts for "
        f"{ratio_pct} of your combined earnings (Debt-to-Income / DTI ratio). "
        f"Additionally, the requested loan represents approximately {loan_years} years of your gross household income."
    )

    if figures.emi_ratio > EMI_HARD_LIMIT:
        lines.append(
            f"Affordability Concern: An EMI taking {ratio_pct} of your income leaves insufficient financial "
            "cushion for basic household living expenses, emergencies, and utility bills. Retail banks enforce a strict "
            f"hard ceiling (normally 50% to 60%) to protect borrowers from debt distress."
        )
    elif figures.emi_ratio > EMI_STRETCH_LIMIT:
        lines.append(
            f"Debt-to-Income Note: At {ratio_pct}, your monthly installment is in the 'stretched' zone. While not "
            "an automatic refusal, lenders will scrutinize other financial obligations closely and may request additional "
            "guarantees or a larger down payment."
        )
    else:
        lines.append(
            f"Affordability Strength: With an EMI consuming only {ratio_pct} of your monthly income, your repayment "
            "obligation is well within banking comfort thresholds (typically up to 40-45%), leaving ample liquidity "
            "for household necessities."
        )

    # 3. Credit Repayment History Impact
    if good_credit:
        lines.append(
            "Credit History Advantage: You have a verified record of meeting past credit obligations on time. "
            "In retail lending, credit history is the single most influential statistical determinant (accounting for "
            "over 30% of the predictive weighting). A clean credit profile demonstrates repayment discipline and "
            "significantly elevates approval confidence."
        )
    else:
        lines.append(
            "Credit History Risk Factor: Your application indicates missing or delayed payments on past credit facilities. "
            "In mortgage underwriting, credit repayment track record is the number-one screening criterion. Lenders view "
            "historical delinquencies as a strong indicator of future default risk, which is often sufficient on its own "
            "to trigger an application decline or require high-risk underwriting scrutiny."
        )

    # 4. Profile & Household Factors
    profile_notes: list[str] = []
    if float(cleaned.get(s.COAPPLICANT_INCOME, 0)) > 0:
        coapp_str = format_inr(float(cleaned[s.COAPPLICANT_INCOME]))
        profile_notes.append(
            f"a supporting co-applicant contributing {coapp_str}/month to your household debt-servicing capacity"
        )
    if cleaned.get(s.EDUCATION) == s.GRADUATE:
        profile_notes.append("graduate education credentials associated with stable long-term earnings potential")
    prop_area = cleaned.get(s.PROPERTY_AREA, "")
    if prop_area:
        profile_notes.append(f"property situated in a {prop_area.lower()} location")

    if profile_notes:
        lines.append(
            "Profile Context: Other contributing elements in your application include "
            + "; ".join(profile_notes)
            + "."
        )

    return "\n\n".join(lines)


def generate_improvement_suggestions(
    cleaned: dict[str, Any],
    figures: Affordability,
    *,
    approved: bool,
    guardrail_applied: bool,
) -> list[ImprovementSuggestion]:
    """Generate specific, actionable recommendations to improve approval prospects."""
    suggestions: list[ImprovementSuggestion] = []
    good_credit = cleaned.get(s.CREDIT_HISTORY) == s.CREDIT_GOOD
    term_months = int(cleaned.get(s.LOAN_TERM, 240))
    current_term_years = term_months // 12
    income = figures.income
    loan = figures.loan
    emi = figures.emi
    emi_ratio = figures.emi_ratio

    if not approved:
        # Suggestion 1: Credit Profile Rehabilitation (if bad credit)
        if not good_credit:
            suggestions.append(
                ImprovementSuggestion(
                    category="Credit Health",
                    title="Rebuild and Clean Your Credit History",
                    description=(
                        "Credit repayment history is the single most critical factor in mortgage approval, "
                        "accounting for nearly a third of the model's decision weight. Any past default or delay "
                        "creates significant friction with automated bank underwriting systems."
                    ),
                    action=(
                        "Request your official CIBIL/Experian credit report and dispute any inaccuracies. Settle any "
                        "pending overdue balances, obtain 'No Due Certificates' (NDCs), and make all utility and credit card "
                        "payments promptly for the next 6 to 12 months before reapplying."
                    ),
                )
            )

        # Suggestion 2: Reduce Loan Amount to Target Safe Affordability
        max_safe_loan = calculate_max_loan(income, term_months, target_dti=TARGET_SAFE_DTI)
        if loan > max_safe_loan and max_safe_loan > 0:
            suggested_amount = round(max_safe_loan / 25000) * 25000  # Round to neat 25k increments
            if suggested_amount < 25000:
                suggested_amount = 25000
            new_emi = estimate_emi(suggested_amount, term_months)
            new_ratio = f"{new_emi / income:.0%}" if income > 0 else "N/A"
            suggestions.append(
                ImprovementSuggestion(
                    category="Loan Sizing",
                    title="Reduce the Requested Loan Amount",
                    description=(
                        f"Your requested loan of {format_inr(loan)} requires an estimated monthly payment of "
                        f"{format_inr(emi)}, which consumes {emi_ratio:.0%} of your monthly income. Lenders prefer "
                        "total loan payments to remain under 40% to 45% of gross earnings."
                    ),
                    action=(
                        f"Reduce your loan request to approximately {format_inr(suggested_amount)}. At this amount, "
                        f"your monthly EMI drops to ~{format_inr(new_emi)} ({new_ratio} of income), bringing your application "
                        "well inside standard banking affordability guidelines."
                    ),
                )
            )

        # Suggestion 3: Extend Loan Tenure (if tenure < 30 years)
        if current_term_years < 30:
            target_tenure_years = 30 if current_term_years <= 20 else 25
            target_tenure_months = target_tenure_years * 12
            extended_emi = estimate_emi(loan, target_tenure_months)
            extended_ratio = extended_emi / income if income > 0 else float("inf")
            pct_diff = ((emi - extended_emi) / emi) if emi > 0 else 0.0

            suggestions.append(
                ImprovementSuggestion(
                    category="Repayment Term",
                    title=f"Extend Repayment Tenure to {target_tenure_years} Years",
                    description=(
                        f"Spreading your repayments over a longer duration reduces the monthly installment. Currently "
                        f"selected for {current_term_years} years, extending the duration provides immediate cash flow relief."
                    ),
                    action=(
                        f"Increase the loan term from {current_term_years} years to {target_tenure_years} years. "
                        f"This lowers your monthly payment from {format_inr(emi)} to ~{format_inr(extended_emi)} "
                        f"(saving {pct_diff:.0%} each month), reducing your debt-to-income ratio to {extended_ratio:.0%}."
                    ),
                )
            )

        # Suggestion 4: Add or Increase Co-Applicant Income
        coapp_income = float(cleaned.get(s.COAPPLICANT_INCOME, 0))
        if emi_ratio > TARGET_SAFE_DTI:
            target_total_income = emi / TARGET_SAFE_DTI
            additional_needed = max(target_total_income - income, 5000.0)
            suggested_add = round(additional_needed / 5000) * 5000

            if coapp_income == 0:
                action_text = (
                    f"Include an earning spouse, parent, or working child as a co-applicant with an income of at least "
                    f"{format_inr(suggested_add)}/month. Combining incomes boosts total repayment capacity and lowers DTI."
                )
            else:
                action_text = (
                    f"Add another earning household member or demonstrate additional steady co-applicant income of "
                    f"~{format_inr(suggested_add)}/month to reach the recommended total household income of {format_inr(target_total_income)}."
                )

            suggestions.append(
                ImprovementSuggestion(
                    category="Household Income",
                    title="Add or Increase Co-Applicant Income",
                    description=(
                        "Banks evaluate the collective household income when assessing repayment capacity. A co-applicant "
                        "shares repayment responsibility, reducing the bank's default exposure."
                    ),
                    action=action_text,
                )
            )

        # Suggestion 5: Increase Down Payment / Self-Contribution
        suggestions.append(
            ImprovementSuggestion(
                category="Down Payment",
                title="Increase Your Upfront Down Payment",
                description=(
                    "Providing a higher initial down payment (e.g., 20% to 30% of the total property valuation) "
                    "lowers the required loan-to-value (LTV) ratio."
                ),
                action=(
                    "Allocate savings or liquidated investments toward a larger down payment. Lowering the principal loan "
                    "requested by even 10-15% directly decreases both EMI burden and interest expense."
                ),
            )
        )

        # Suggestion 6: Clear Existing Short-Term Liabilities
        suggestions.append(
            ImprovementSuggestion(
                category="Debt Management",
                title="Consolidate or Pay Off Existing Short-Term Debts",
                description=(
                    "Underwriters examine total Debt-to-Income across all credit channels, including personal loans, "
                    "two-wheeler loans, consumer EMIs, and active credit card revolving balances."
                ),
                action=(
                    "Clear active high-interest personal loans or credit card balances before submitting your mortgage application. "
                    "Eliminating existing monthly obligations frees up disposable income for the home loan."
                ),
            )
        )

    else:
        # Suggestions for APPROVED applicants to maintain qualification
        suggestions.append(
            ImprovementSuggestion(
                category="Credit Maintenance",
                title="Maintain Spotless Credit Discipline",
                description=(
                    "Lenders pull a fresh credit bureau report right before final disbursement. Any new inquiry, loan application, "
                    "or missed payment can stall or cancel formal approval."
                ),
                action=(
                    "Avoid applying for new credit cards, personal loans, or buying expensive items on EMI until your home loan "
                    "has been fully sanctioned and disbursed."
                ),
            )
        )
        suggestions.append(
            ImprovementSuggestion(
                category="Documentation",
                title="Organize Financial and Property Records",
                description=(
                    "Speed up underwriting by preparing standard required paperwork in advance."
                ),
                action=(
                    "Assemble 6 months of bank account statements, 3 months of salary slips, Form 16 / ITR filings for the last "
                    "2 years, along with clear property title deeds and approved construction plans."
                ),
            )
        )
        suggestions.append(
            ImprovementSuggestion(
                category="Rate Optimization",
                title="Compare and Negotiate Interest Rates",
                description=(
                    "Because your application presents a strong credit profile and healthy affordability ratios, you are in an "
                    "advantageous bargaining position."
                ),
                action=(
                    "Compare offers from multiple leading lenders. Even a 0.25% to 0.50% interest rate reduction can save you "
                    "several lakhs in interest over the life of your home loan."
                ),
            )
        )

    return suggestions
