"""Layer 2: validation of raw form answers."""

from __future__ import annotations

import unittest

from loanwise.domain.formatting import format_inr
from loanwise.domain.validation import validate_application
from tests.helpers import good_form


class ValidationTests(unittest.TestCase):
    def test_valid_form_passes(self):
        r = validate_application(good_form())
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.cleaned["applicant_income"], 20000)
        self.assertEqual(r.cleaned["credit_history"], "good")

    def test_case_and_whitespace_forgiven(self):
        r = validate_application(
            good_form(
                gender=" male ",
                married=" YES ",
                education="not graduate",
                self_employed="No",
                property_area="SEMI-URBAN",
            )
        )
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.cleaned["gender"], "Male")
        self.assertEqual(r.cleaned["married"], "Yes")
        self.assertEqual(r.cleaned["education"], "Not Graduate")
        self.assertEqual(r.cleaned["property_area"], "Semiurban")

    def test_dependents_variants(self):
        for raw, want in [
            ("3+", "3+"),
            ("3", "3+"),
            ("4", "3+"),
            (5, "3+"),
            (" 2 ", "2"),
            (0, "0"),
            ("none", "0"),
        ]:
            r = validate_application(good_form(dependents=raw))
            self.assertTrue(r.ok, (raw, r.errors))
            self.assertEqual(r.cleaned["dependents"], want, raw)

    def test_dependents_rejects_garbage(self):
        for raw in ["-1", "1.5", "lots", True, 999]:
            r = validate_application(good_form(dependents=raw))
            self.assertIn("dependents", r.errors, raw)

    def test_number_formatting_forgiven(self):
        for raw, want in [
            ("25,000", 25000),
            ("₹ 25000", 25000),
            ("Rs. 25,000", 25000),
            ("25000 ", 25000),
            ("25 000", 25000),
            ("25k", 25000),
            (25000.5, 25000.5),
        ]:
            r = validate_application(good_form(applicant_income=raw))
            self.assertTrue(r.ok, (raw, r.errors))
            self.assertEqual(r.cleaned["applicant_income"], want, raw)

    def test_lakh_loan_amount_with_note(self):
        r = validate_application(good_form(loan_amount="5 lakh"))
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.cleaned["loan_amount"], 500000)
        self.assertTrue(any("5 lakh" in w for w in r.warnings))

    def test_credit_history_yes_no_bool(self):
        for raw, want in [
            ("yes", "good"),
            ("NO", "bad"),
            (True, "good"),
            (False, "bad"),
            ("Good", "good"),
            (" bad ", "bad"),
            (1, "good"),
            (0, "bad"),
        ]:
            r = validate_application(good_form(credit_history=raw))
            self.assertTrue(r.ok, (raw, r.errors))
            self.assertEqual(r.cleaned["credit_history"], want, raw)

    def test_missing_fields_all_reported_at_once(self):
        r = validate_application({})
        # coapplicant_income blank is treated as 0, everything else is required
        expected = {
            "gender",
            "married",
            "dependents",
            "education",
            "self_employed",
            "applicant_income",
            "loan_amount",
            "loan_term",
            "credit_history",
            "property_area",
        }
        self.assertEqual(set(r.errors), expected)
        for msg in r.errors.values():
            self.assertTrue(msg.startswith("This answer is missing."), msg)

    def test_non_numeric_text_rejected(self):
        r = validate_application(good_form(applicant_income="lots of money"))
        self.assertEqual(
            r.errors["applicant_income"],
            "Please type your monthly income using numbers only, like 25000.",
        )

    def test_negative_numbers_rejected(self):
        r = validate_application(
            good_form(applicant_income=-5, loan_amount="-100000", coapplicant_income=-1)
        )
        for f in ("applicant_income", "loan_amount", "coapplicant_income"):
            self.assertIn("negative", r.errors[f])

    def test_nan_and_infinity_rejected(self):
        for bad in [float("nan"), float("inf"), "NaN", "Infinity", "inf", 1e400]:
            r = validate_application(good_form(applicant_income=bad))
            self.assertIn("applicant_income", r.errors, bad)

    def test_absurd_magnitudes_rejected(self):
        r = validate_application(good_form(applicant_income=10**12, loan_amount=10**9))
        self.assertIn("too big", r.errors["applicant_income"])
        self.assertIn("biggest loan", r.errors["loan_amount"])
        r = validate_application(good_form(loan_amount=10))
        self.assertIn("smallest loan", r.errors["loan_amount"])

    def test_booleans_as_numbers_rejected(self):
        r = validate_application(
            good_form(applicant_income=True, loan_amount=False, loan_term=True)
        )
        self.assertIn("applicant_income", r.errors)
        self.assertIn("loan_amount", r.errors)
        self.assertIn("loan_term", r.errors)

    def test_unknown_enum_values_rejected(self):
        r = validate_application(
            good_form(
                gender="robot",
                property_area="Mars",
                married="maybe",
                education="PhD-ish",
                self_employed="sometimes",
            )
        )
        self.assertEqual(
            set(r.errors), {"gender", "property_area", "married", "education", "self_employed"}
        )
        self.assertEqual(r.errors["gender"], "Please choose Male or Female.")

    def test_loan_term_rules(self):
        for ok_term, want in [
            (360, 360),
            ("360", 360),
            ("360 months", 360),
            (360.0, 360),
            ("30 years", 360),
            ("12", 12),
        ]:
            r = validate_application(good_form(loan_term=ok_term))
            self.assertTrue(r.ok, (ok_term, r.errors))
            self.assertEqual(r.cleaned["loan_term"], want)
        for bad in [350, 0, -360, "forever", 360.5, [360], None]:
            r = validate_application(good_form(loan_term=bad))
            self.assertIn("loan_term", r.errors, bad)

    def test_both_incomes_zero_rejected(self):
        r = validate_application(good_form(applicant_income=0, coapplicant_income=0))
        self.assertIn("At least one person must have some income", r.errors["applicant_income"])

    def test_zero_applicant_with_coapplicant_ok(self):
        r = validate_application(good_form(applicant_income=0, coapplicant_income=20000))
        self.assertTrue(r.ok, r.errors)

    def test_blank_coapplicant_means_zero(self):
        for blank in [None, "", "   "]:
            form = good_form(coapplicant_income=blank)
            r = validate_application(form)
            self.assertTrue(r.ok, r.errors)
            self.assertEqual(r.cleaned["coapplicant_income"], 0.0)

    def test_extra_fields_ignored(self):
        r = validate_application(good_form(hacker="DROP TABLE", __proto__={"x": 1}))
        self.assertTrue(r.ok, r.errors)
        self.assertNotIn("hacker", r.cleaned)

    def test_non_object_payloads(self):
        for p in [None, [], ["a"], "hello", 42, True]:
            r = validate_application(p)
            self.assertFalse(r.ok)
            self.assertIn("_form", r.errors)

    def test_lists_and_objects_in_fields_rejected(self):
        r = validate_application(good_form(gender=["Male"], applicant_income={"v": 1}))
        self.assertIn("gender", r.errors)
        self.assertIn("applicant_income", r.errors)

    def test_format_inr(self):
        self.assertEqual(format_inr(500000), "₹5,00,000")
        self.assertEqual(format_inr(10000000), "₹1,00,00,000")
        self.assertEqual(format_inr(999), "₹999")


if __name__ == "__main__":
    unittest.main()
