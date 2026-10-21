"""HTTP API behaviour with fake, broken, missing and real models."""

from __future__ import annotations

import math
import unittest

from loanwise.domain.schemas import MODEL_COLUMNS
from loanwise.domain.validation import validate_application
from tests.helpers import (
    HAS_MODEL,
    SKIP_NO_MODEL,
    ApiTestCase,
    BrokenModel,
    FakeModel,
    good_form,
)


class FakeModelApiTests(ApiTestCase):
    model = FakeModel()

    def test_predict_valid(self):
        r = self.client.post("/api/predict", json=good_form())
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        for key in (
            "ok",
            "approved",
            "verdict",
            "headline",
            "confidence",
            "confidence_label",
            "reasons",
            "warnings",
            "guardrail_applied",
            "emi_estimate",
            "id",
        ):
            self.assertIn(key, b)
        self.assertTrue(b["approved"])
        self.assertEqual(b["verdict"], "Likely Approved")
        self.assertAlmostEqual(b["confidence"], 0.9)
        self.assertIsInstance(b["id"], int)

    def test_predict_sends_contract_frame_to_model(self):
        self.client.post("/api/predict", json=good_form(loan_amount="₹ 1,28,000", dependents="3"))
        row = self.model.last_frame.iloc[0]
        self.assertEqual(list(self.model.last_frame.columns), list(MODEL_COLUMNS))
        self.assertEqual(row["LoanAmount"], 128.0)
        self.assertEqual(row["Dependents"], "3+")

    def test_predict_formatting_forgiven(self):
        form = good_form(
            gender=" female",
            married="no",
            applicant_income="₹ 25,000",
            loan_amount="2 lakh",
            credit_history="YES",
            dependents="5",
            property_area="rural",
            loan_term="15 years",
            extra="ignored",
        )
        r = self.client.post("/api/predict", json=form)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertTrue(r.get_json()["warnings"])

    def test_predict_garbage_returns_422_with_all_errors(self):
        r = self.client.post(
            "/api/predict",
            json={
                "gender": "dog",
                "applicant_income": "abc",
                "loan_amount": -1,
                "loan_term": 7,
                "credit_history": "maybe",
            },
        )
        self.assertEqual(r.status_code, 422)
        b = r.get_json()
        self.assertFalse(b["ok"])
        self.assertEqual(b["message"], "Some answers need fixing. Look for the red boxes.")
        self.assertGreaterEqual(len(b["errors"]), 8)

    def test_malformed_json_400(self):
        for body in ["{not json", "", "   ", "\xff\xfe"]:
            r = self.client.post("/api/predict", data=body, content_type="application/json")
            self.assertEqual(r.status_code, 400, body)
            self.assert_friendly(r.get_json())

    def test_non_object_json_400(self):
        for body in ["[1,2,3]", '"hello"', "42", "null", "true"]:
            r = self.client.post("/api/predict", data=body, content_type="application/json")
            self.assertEqual(r.status_code, 400, body)
            self.assert_friendly(r.get_json())

    def test_nan_literal_in_json_rejected(self):
        body = (
            '{"gender":"Male","married":"Yes","dependents":"0","education":"Graduate",'
            '"self_employed":"No","applicant_income":NaN,"coapplicant_income":Infinity,'
            '"loan_amount":500000,"loan_term":360,"credit_history":"good","property_area":"Urban"}'
        )
        r = self.client.post("/api/predict", data=body, content_type="application/json")
        self.assertEqual(r.status_code, 422)
        self.assertIn("applicant_income", r.get_json()["errors"])
        self.assertIn("coapplicant_income", r.get_json()["errors"])

    def test_guardrail_override_via_api(self):
        r = self.client.post(
            "/api/predict",
            json=good_form(applicant_income=3000, coapplicant_income=0, loan_amount=5_000_000),
        )
        b = r.get_json()
        self.assertEqual(r.status_code, 200)
        self.assertFalse(b["approved"])
        self.assertTrue(b["guardrail_applied"])

    def test_request_too_large_413(self):
        r = self.client.post(
            "/api/predict", data="{" + " " * 100_000 + "}", content_type="application/json"
        )
        self.assertEqual(r.status_code, 413)
        self.assert_friendly(r.get_json())

    def test_form_encoded_post_works(self):
        r = self.client.post("/api/predict", data={k: str(v) for k, v in good_form().items()})
        self.assertEqual(r.status_code, 200, r.get_json())

    def test_health(self):
        self.assertEqual(
            self.client.get("/api/health").get_json(), {"ok": True, "model_loaded": True}
        )

    def test_sample_is_valid_request(self):
        for _ in range(25):
            b = self.client.get("/api/sample").get_json()
            self.assertTrue(b["ok"])
            fields = b["sample"]
            r = validate_application(fields)
            self.assertTrue(r.ok, (fields, r.errors))
            for v in fields.values():
                self.assertFalse(isinstance(v, float) and math.isnan(v))

    def test_api_404_and_405_json(self):
        r = self.client.get("/api/does-not-exist")
        self.assertEqual(r.status_code, 404)
        self.assert_friendly(r.get_json())
        r = self.client.get("/api/predict")
        self.assertEqual(r.status_code, 405)
        self.assert_friendly(r.get_json())

    def test_cors_for_localhost(self):
        r = self.client.get("/api/health", headers={"Origin": "http://localhost:5173"})
        self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "http://localhost:5173")
        r = self.client.get("/api/health", headers={"Origin": "https://evil.example"})
        self.assertIsNone(r.headers.get("Access-Control-Allow-Origin"))

    def test_spa_fallback_without_dist(self):
        r = self.client.get("/some/page")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"built", r.data)

    def test_spa_serves_dist(self):
        dist = self.settings.frontend_dist
        (dist / "assets").mkdir(parents=True)
        (dist / "index.html").write_text("<div id=root>INDEX</div>")
        (dist / "assets" / "app.js").write_text("console.log(1)")
        for path, expected in [
            ("/history", b"INDEX"),
            ("/assets/app.js", b"console.log"),
            ("/../../etc/passwd", b"INDEX"),
        ]:
            with self.client.get(path) as r:
                self.assertIn(expected, r.data, path)


class BrokenModelApiTests(ApiTestCase):
    model = BrokenModel()

    def test_model_crash_is_friendly_500(self):
        r = self.client.post("/api/predict", json=good_form())
        self.assertEqual(r.status_code, 500)
        self.assert_friendly(r.get_json())


class NoModelApiTests(ApiTestCase):
    def settings_overrides(self):
        return {
            "model_path": self.tmp / "missing.pkl",
            "model_info_path": self.tmp / "missing.json",
        }

    def test_missing_model_503(self):
        r = self.client.post("/api/predict", json=good_form())
        self.assertEqual(r.status_code, 503)
        self.assert_friendly(r.get_json())
        self.assertFalse(self.client.get("/api/health").get_json()["model_loaded"])
        self.assertEqual(self.client.get("/api/model-info").status_code, 503)

    def test_validation_still_runs_without_model(self):
        r = self.client.post("/api/predict", json={"gender": "x"})
        self.assertEqual(r.status_code, 422)


@unittest.skipUnless(HAS_MODEL, SKIP_NO_MODEL)
class RealModelApiTests(ApiTestCase):
    model = None  # load the real file

    def test_health_model_loaded(self):
        self.assertTrue(self.client.get("/api/health").get_json()["model_loaded"])

    def test_model_info(self):
        b = self.client.get("/api/model-info").get_json()
        self.assertTrue(b["ok"])
        self.assertIn("chosen_model", b)

    def test_strong_applicant_approved(self):
        b = self.client.post("/api/predict", json=good_form()).get_json()
        self.assertTrue(b["ok"])
        self.assertTrue(b["approved"], b)
        self.assertIn(b["confidence_label"], {"High", "Medium", "Low"})
        self.assertTrue(0.5 <= b["confidence"] <= 1.0)

    def test_bad_credit_rejected(self):
        b = self.client.post("/api/predict", json=good_form(credit_history="bad")).get_json()
        self.assertFalse(b["approved"], b)

    def test_absurd_loan_rejected_by_guardrail(self):
        b = self.client.post(
            "/api/predict",
            json=good_form(applicant_income=2000, coapplicant_income=0, loan_amount=10_000_000),
        ).get_json()
        self.assertFalse(b["approved"])
        self.assertTrue(b["guardrail_applied"])

    def test_extreme_income_still_sensible(self):
        b = self.client.post(
            "/api/predict", json=good_form(applicant_income=9_000_000, loan_amount=100000)
        ).get_json()
        self.assertTrue(b["ok"])
        self.assertTrue(b["approved"], b)
        self.assertTrue(b["warnings"])

    def test_many_samples_predict(self):
        for _ in range(20):
            fields = self.client.get("/api/sample").get_json()["sample"]
            r = self.client.post("/api/predict", json=fields)
            self.assertEqual(r.status_code, 200, r.get_json())


if __name__ == "__main__":
    unittest.main()
