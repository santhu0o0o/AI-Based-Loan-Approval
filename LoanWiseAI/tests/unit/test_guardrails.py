"""Guardrails: lending rules applied on top of the model."""

from __future__ import annotations

import unittest

from loanwise.domain.guardrails import apply_guardrails, confidence_label, estimate_emi
from loanwise.domain.validation import validate_application
from tests.helpers import good_form


class GuardrailTests(unittest.TestCase):
    def cleaned(self, **kw):
        r = validate_application(good_form(**kw))
        assert r.ok, r.errors
        return r.cleaned

    def test_emi_formula(self):
        # ₹1,00,000 at 9% for 12 months ≈ ₹8,745
        self.assertAlmostEqual(estimate_emi(100000, 12), 8745.2, delta=1)

    def test_confidence_labels(self):
        self.assertEqual(confidence_label(0.75), "High")
        self.assertEqual(confidence_label(0.6), "Medium")
        self.assertEqual(confidence_label(0.59), "Low")

    def test_model_approval_kept_when_sensible(self):
        d = apply_guardrails(self.cleaned(), 0.84)
        self.assertTrue(d.approved)
        self.assertFalse(d.guardrail_applied)
        self.assertEqual(d.verdict, "Likely Approved")
        self.assertEqual(d.confidence_label, "High")
        self.assertTrue(3 <= len(d.reasons) <= 5)
        self.assertIn(
            {"type": "positive", "text": "Your credit history is good — this helps a lot."},
            d.reasons,
        )

    def test_unaffordable_emi_overrides_approval(self):
        # ₹20,000/month income, ₹10 lakh over 12 months -> EMI ≈ ₹87k
        d = apply_guardrails(
            self.cleaned(
                applicant_income=20000, coapplicant_income=0, loan_amount=1_000_000, loan_term=12
            ),
            0.95,
        )
        self.assertFalse(d.approved)
        self.assertTrue(d.guardrail_applied)
        self.assertEqual(d.verdict, "Likely Rejected")
        self.assertGreaterEqual(d.confidence, 0.9)
        self.assertEqual(d.reasons[0]["type"], "negative")

    def test_loan_multiple_overrides_approval(self):
        # ₹5,000/month, ₹1 crore over 40 years: EMI ~ ₹77k and 2000x income
        d = apply_guardrails(
            self.cleaned(
                applicant_income=5000, coapplicant_income=0, loan_amount=10_000_000, loan_term=480
            ),
            0.99,
        )
        self.assertFalse(d.approved)
        self.assertTrue(d.guardrail_applied)
        self.assertTrue(any("years of your total income" in r["text"] for r in d.reasons))

    def test_bad_credit_flagged_and_capped(self):
        d = apply_guardrails(self.cleaned(credit_history="bad"), 0.95)
        self.assertTrue(
            any(r["type"] == "negative" and "credit history is bad" in r["text"] for r in d.reasons)
        )
        self.assertLessEqual(d.confidence, 0.65)

    def test_never_upgrades_rejection(self):
        d = apply_guardrails(self.cleaned(), 0.2)
        self.assertFalse(d.approved)
        self.assertFalse(d.guardrail_applied)
        self.assertAlmostEqual(d.confidence, 0.8)

    def test_reasons_count_bounds(self):
        d = apply_guardrails(
            self.cleaned(
                applicant_income=1000,
                coapplicant_income=500,
                loan_amount=10_000_000,
                loan_term=12,
                credit_history="bad",
            ),
            0.5,
        )
        self.assertTrue(3 <= len(d.reasons) <= 5)
        for r in d.reasons:
            self.assertIn(r["type"], {"positive", "negative", "neutral"})
            self.assertTrue(r["text"])


if __name__ == "__main__":
    unittest.main()
