"""Integration tests for PDF report generation and download endpoints."""

from __future__ import annotations

import io
import unittest

from tests.helpers import ApiTestCase, FakeModel, good_form


class ReportEndpointTests(ApiTestCase):
    model = FakeModel(0.88, 0.12)

    def test_post_report_pdf_with_answers_and_result(self):
        form = good_form(applicant_income=50000, loan_amount=1500000, loan_term=240)
        predict_res = self.client.post("/api/predict", json=form)
        self.assertEqual(predict_res.status_code, 200)
        pred_data = predict_res.get_json()

        pdf_req = {
            "answers": form,
            "result": pred_data,
            "id": pred_data.get("id"),
        }
        res = self.client.post("/api/report/pdf", json=pdf_req)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertIn("attachment", res.headers.get("Content-Disposition", ""))
        self.assertTrue(res.data.startswith(b"%PDF"))

    def test_post_report_pdf_by_id(self):
        form = good_form(applicant_income=45000, loan_amount=1200000)
        predict_res = self.client.post("/api/predict", json=form)
        pred_id = predict_res.get_json()["id"]
        self.assertIsNotNone(pred_id)

        res = self.client.post("/api/report/pdf", json={"id": pred_id})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF"))

    def test_get_history_pdf(self):
        form = good_form(applicant_income=40000, loan_amount=1000000)
        predict_res = self.client.post("/api/predict", json=form)
        pred_id = predict_res.get_json()["id"]

        res = self.client.get(f"/api/history/{pred_id}/pdf")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF"))

    def test_get_history_pdf_not_found(self):
        res = self.client.get("/api/history/999999/pdf")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
