"""Service layer: prediction orchestration, model registry and sample generation."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from loanwise.domain.validation import validate_application
from loanwise.services.model_info import load_model_info
from loanwise.services.model_registry import ModelRegistry, StaticModelProvider
from loanwise.services.prediction_service import (
    InvalidApplicationError,
    ModelPredictionError,
    ModelUnavailableError,
    PredictionService,
)
from loanwise.services.sample_service import (
    SampleService,
    SampleUnavailableError,
    row_to_application,
)
from loanwise.storage.history_repository import HistoryRepository
from tests.helpers import BrokenModel, FakeModel, good_form


class _NoModel:
    def get(self) -> None:
        return None


class _NanModel:
    def predict_proba(self, X: Any) -> np.ndarray:
        return np.array([[np.nan, np.nan]])


class _FailingHistory(HistoryRepository):
    def add(self, *args: Any, **kwargs: Any) -> int:
        raise OSError("disk full")


class _TempDirCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.history = HistoryRepository(self.tmp / "h.db")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class PredictionServiceTests(_TempDirCase):
    def service(self, model: Any = None) -> PredictionService:
        return PredictionService(StaticModelProvider(model or FakeModel()), self.history)

    def test_success_is_saved_with_raw_probability(self) -> None:
        result = self.service().predict(good_form())
        self.assertTrue(result.decision.approved)
        self.assertIsInstance(result.id, int)
        body = result.to_response()
        self.assertEqual(next(iter(body)), "ok")
        self.assertEqual(list(body)[-1], "id")
        self.assertNotIn("model_probability", body)
        self.assertEqual(result.to_record()["model_probability"], 0.9)
        self.assertEqual(self.history.list_recent()[0]["id"], result.id)

    def test_invalid_application_raises_with_all_errors(self) -> None:
        with self.assertRaises(InvalidApplicationError) as ctx:
            self.service().predict({"gender": "dog"})
        self.assertIn("gender", ctx.exception.errors)
        self.assertEqual(self.history.list_recent(), [])

    def test_validation_runs_before_model_lookup(self) -> None:
        service = PredictionService(_NoModel(), self.history)
        with self.assertRaises(InvalidApplicationError):
            service.predict({})
        with self.assertRaises(ModelUnavailableError):
            service.predict(good_form())
        self.assertFalse(service.model_loaded())

    def test_model_errors_and_nan_become_model_failure(self) -> None:
        for model in (BrokenModel(), _NanModel()):
            with self.assertRaises(ModelPredictionError), self.assertLogs("loanwise", "ERROR"):
                self.service(model).predict(good_form())

    def test_history_failure_does_not_fail_prediction(self) -> None:
        service = PredictionService(
            StaticModelProvider(FakeModel()), _FailingHistory(self.tmp / "f.db")
        )
        with self.assertLogs("loanwise", "ERROR"):
            result = service.predict(good_form())
        self.assertIsNone(result.id)
        self.assertTrue(result.decision.approved)


class ModelRegistryTests(_TempDirCase):
    def test_missing_file_returns_none(self) -> None:
        self.assertIsNone(ModelRegistry(self.tmp / "nope.pkl").get())

    def test_loads_lazily_and_keeps_model_when_file_removed(self) -> None:
        path = self.tmp / "m.pkl"
        joblib.dump(FakeModel(), path)
        registry = ModelRegistry(path)
        first = registry.get()
        self.assertIsNotNone(first)
        self.assertIs(registry.get(), first)  # cached while the file is unchanged
        path.unlink()
        self.assertIs(registry.get(), first)

    def test_rejects_objects_without_predict_proba(self) -> None:
        path = self.tmp / "bad.pkl"
        joblib.dump({"not": "a model"}, path)
        with self.assertLogs("loanwise", "ERROR"):
            self.assertIsNone(ModelRegistry(path).get())


class SampleAndInfoTests(_TempDirCase):
    def test_blank_cells_are_filled_with_valid_defaults(self) -> None:
        fields = row_to_application(
            {
                "Loan_Amount_Term": 350.0,
                "Dependents": "7",
                "ApplicantIncome": 0.0,
                "CoapplicantIncome": float("nan"),
                "Credit_History": 0.0,
                "Gender": "  ",
            }
        )
        self.assertEqual(fields["loan_term"], 360)
        self.assertEqual(fields["dependents"], "0")
        self.assertEqual(fields["applicant_income"], 3800)
        self.assertEqual(fields["credit_history"], "bad")
        self.assertEqual(fields["gender"], "Male")
        self.assertEqual(fields["loan_amount"], 128000)
        self.assertTrue(validate_application(fields).ok)

    def test_missing_csv_raises_sample_unavailable(self) -> None:
        with self.assertRaises(SampleUnavailableError), self.assertLogs("loanwise", "ERROR"):
            SampleService(self.tmp / "missing.csv").random_application()

    def test_model_info_reading(self) -> None:
        path = self.tmp / "info.json"
        self.assertIsNone(load_model_info(path))
        path.write_text("[1, 2]", encoding="utf-8")
        self.assertEqual(load_model_info(path), {"data": [1, 2]})
        path.write_text("{broken", encoding="utf-8")
        self.assertIsNone(load_model_info(path))


if __name__ == "__main__":
    unittest.main()
