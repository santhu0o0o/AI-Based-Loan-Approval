"""Layer 3: mapping validated answers onto the model's input frame."""

from __future__ import annotations

import unittest

from loanwise.domain.guardrails import apply_guardrails
from loanwise.domain.sanitizer import to_model_frame
from loanwise.domain.schemas import MODEL_COLUMNS
from loanwise.domain.validation import validate_application
from tests.helpers import good_form


class SanitizerTests(unittest.TestCase):
    def test_frame_columns_and_units(self):
        r = validate_application(good_form(credit_history="bad", dependents="4"))
        s = to_model_frame(r.cleaned)
        self.assertEqual(list(s.frame.columns), list(MODEL_COLUMNS))
        row = s.frame.iloc[0]
        self.assertEqual(row["LoanAmount"], 500.0)  # ₹5,00,000 -> 500 thousand
        self.assertEqual(row["Credit_History"], 0.0)
        self.assertEqual(row["Dependents"], "3+")
        self.assertEqual(row["Loan_Amount_Term"], 360.0)
        self.assertEqual(s.warnings, [])

    def test_real_amounts_passed_through(self):
        # model is monotonic in the EMI-to-income ratio, so no clamping is done
        r = validate_application(
            good_form(applicant_income=5_000_000, coapplicant_income=900_000, loan_amount=9_000_000)
        )
        s = to_model_frame(r.cleaned)
        row = s.frame.iloc[0]
        self.assertEqual(row["ApplicantIncome"], 5_000_000.0)
        self.assertEqual(row["CoapplicantIncome"], 900_000.0)
        self.assertEqual(row["LoanAmount"], 9000.0)
        self.assertEqual(len(s.warnings), 1)
        self.assertIn("MONTHLY", s.warnings[0])  # ₹59 lakh/month looks like a typo

    def test_guardrails_judge_huge_loan(self):
        r = validate_application(
            good_form(
                applicant_income=30000, coapplicant_income=0, loan_amount=9_000_000, loan_term=120
            )
        )
        d = apply_guardrails(r.cleaned, 0.9)
        self.assertTrue(d.guardrail_applied)
        self.assertFalse(d.approved)

    def test_small_loan_no_warning(self):
        r = validate_application(good_form(loan_amount=2000))
        s = to_model_frame(r.cleaned)
        self.assertEqual(s.frame.iloc[0]["LoanAmount"], 2.0)
        self.assertEqual(s.warnings, [])


if __name__ == "__main__":
    unittest.main()
