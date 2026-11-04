"""Tests for financial analysis, detailed explanations, and improvement suggestions."""

from __future__ import annotations

import unittest

from loanwise.domain.analysis import (
    calculate_max_loan,
    compute_financial_metrics,
    generate_detailed_explanation,
    generate_improvement_suggestions,
)
from loanwise.domain.guardrails import assess_affordability
from loanwise.domain.validation import validate_application
from tests.helpers import good_form


class AnalysisTests(unittest.TestCase):
    def cleaned(self, **kw):
        r = validate_application(good_form(**kw))
        assert r.ok, r.errors
        return r.cleaned

    def test_calculate_max_loan(self):
        # Income 50,000, 20 years (240 mo) -> reasonable max loan
        loan = calculate_max_loan(50000, 240, target_dti=0.40)
        self.assertGreater(loan, 1_500_000)
        self.assertLess(loan, 3_000_000)

    def test_financial_metrics_computation(self):
        cleaned = self.cleaned(applicant_income=50000, coapplicant_income=20000, loan_amount=2000000, loan_term=240)
        figures = assess_affordability(cleaned)
        metrics = compute_financial_metrics(cleaned, figures)

        self.assertEqual(metrics["total_income"], 70000)
        self.assertEqual(metrics["loan_amount"], 2000000)
        self.assertEqual(metrics["loan_term_years"], 20.0)
        self.assertIn("affordability_band", metrics)
        self.assertIn(metrics["affordability_band"], {"Comfortable", "Manageable", "Stretched", "Critical / Unaffordable"})
        self.assertGreater(metrics["max_safe_loan_amount"], 0)

    def test_detailed_explanation_approved(self):
        cleaned = self.cleaned(applicant_income=50000, coapplicant_income=20000, loan_amount=1500000, loan_term=240)
        figures = assess_affordability(cleaned)
        text = generate_detailed_explanation(
            cleaned,
            figures,
            approved=True,
            guardrail_applied=False,
            confidence=0.85,
            confidence_label="High",
            p_approve=0.85,
        )
        self.assertIn("LIKELY APPROVED", text)
        self.assertIn("Affordability", text)
        self.assertIn("Credit History", text)

    def test_detailed_explanation_rejected_guardrail(self):
        cleaned = self.cleaned(applicant_income=5000, coapplicant_income=0, loan_amount=5000000, loan_term=120)
        figures = assess_affordability(cleaned)
        text = generate_detailed_explanation(
            cleaned,
            figures,
            approved=False,
            guardrail_applied=True,
            confidence=0.92,
            confidence_label="High",
            p_approve=0.08,
        )
        self.assertIn("LIKELY REJECTED", text)
        self.assertIn("guardrails", text.lower())

    def test_improvement_suggestions_rejected_unaffordable(self):
        cleaned = self.cleaned(
            applicant_income=20000,
            coapplicant_income=0,
            loan_amount=3000000,
            loan_term=120,
            credit_history="bad",
        )
        figures = assess_affordability(cleaned)
        suggestions = generate_improvement_suggestions(
            cleaned,
            figures,
            approved=False,
            guardrail_applied=True,
        )
        self.assertGreaterEqual(len(suggestions), 3)

        categories = [s["category"] for s in suggestions]
        self.assertIn("Credit Health", categories)
        self.assertIn("Loan Sizing", categories)
        self.assertIn("Repayment Term", categories)

        for s in suggestions:
            self.assertTrue(s["title"])
            self.assertTrue(s["description"])
            self.assertTrue(s["action"])

    def test_improvement_suggestions_approved(self):
        cleaned = self.cleaned(applicant_income=60000, coapplicant_income=30000, loan_amount=1500000, loan_term=240)
        figures = assess_affordability(cleaned)
        suggestions = generate_improvement_suggestions(
            cleaned,
            figures,
            approved=True,
            guardrail_applied=False,
        )
        self.assertGreaterEqual(len(suggestions), 2)
        categories = [s["category"] for s in suggestions]
        self.assertIn("Credit Maintenance", categories)


if __name__ == "__main__":
    unittest.main()
