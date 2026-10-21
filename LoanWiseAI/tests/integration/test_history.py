"""``/api/history``: predictions are recorded, listed and cleared."""

from __future__ import annotations

import unittest

from tests.helpers import ApiTestCase, FakeModel, good_form


class HistoryApiTests(ApiTestCase):
    model = FakeModel()

    def test_history_roundtrip_and_clear(self):
        self.client.post("/api/predict", json=good_form())
        self.client.post("/api/predict", json=good_form(credit_history="bad"))
        b = self.client.get("/api/history").get_json()
        self.assertTrue(b["ok"])
        self.assertEqual(len(b["items"]), 2)
        newest = b["items"][0]
        for key in ("id", "created_at", "inputs", "approved", "verdict", "confidence"):
            self.assertIn(key, newest)
        self.assertEqual(newest["inputs"]["credit_history"], "bad")
        self.assertFalse(newest["approved"])
        self.assertEqual(len(self.client.get("/api/history?limit=1").get_json()["items"]), 1)
        self.assertEqual(self.client.get("/api/history?limit=abc").status_code, 200)
        self.assertEqual(self.client.delete("/api/history").get_json(), {"ok": True})
        self.assertEqual(self.client.get("/api/history").get_json()["items"], [])

    def test_failed_validation_not_saved(self):
        self.client.post("/api/predict", json={"gender": "x"})
        self.assertEqual(self.client.get("/api/history").get_json()["items"], [])


if __name__ == "__main__":
    unittest.main()
