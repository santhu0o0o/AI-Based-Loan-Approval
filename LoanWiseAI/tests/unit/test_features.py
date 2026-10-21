"""Pipeline feature transforms, schema consistency and the model's monotonicity."""

from __future__ import annotations

import unittest

import joblib
import numpy as np
import pandas as pd

from loanwise.domain import schemas
from loanwise.domain.validation import CHOICE_SYNONYMS
from loanwise.ml.evaluation import check_monotonicity, choose_model
from loanwise.ml.features import (
    RAW_COLS,
    add_engineered_features,
    coerce_raw_input,
    friendly_name,
)
from tests.helpers import DEFAULT_SETTINGS, HAS_MODEL, SKIP_NO_MODEL


class FeatureTransformTests(unittest.TestCase):
    def test_coerce_keeps_contract_columns_and_types(self) -> None:
        raw = pd.DataFrame(
            [
                {
                    "Dependents": 0,
                    "Gender": " Male ",
                    "ApplicantIncome": "abc",
                    "Married": "",
                    "Extra": 1,
                }
            ]
        )
        out = coerce_raw_input(raw)
        self.assertEqual(list(out.columns), RAW_COLS)
        self.assertEqual(out.loc[0, "Dependents"], "0")
        self.assertEqual(out.loc[0, "Gender"], "Male")
        self.assertTrue(np.isnan(out.loc[0, "ApplicantIncome"]))
        self.assertTrue(pd.isna(out.loc[0, "Married"]))

    def test_engineered_ratio_is_clipped_and_safe(self) -> None:
        frame = pd.DataFrame(
            {
                "ApplicantIncome": [5000.0, 0.0],
                "CoapplicantIncome": [0.0, 0.0],
                "LoanAmount": [120.0, 9000.0],
                "Loan_Amount_Term": [360.0, 0.0],
            }
        )
        out = add_engineered_features(frame)
        self.assertAlmostEqual(out.loc[0, "EMI"], 120_000 / 360)
        self.assertAlmostEqual(out.loc[1, "Log_EMI_Income_Ratio"], np.log1p(10.0))

    def test_friendly_names(self) -> None:
        self.assertEqual(friendly_name("Property_Area_Urban"), "Property Area")
        self.assertEqual(friendly_name("Log_EMI_Income_Ratio"), "EMI-to-Income Ratio")
        self.assertEqual(friendly_name("Unknown"), "Unknown")


class SchemaConsistencyTests(unittest.TestCase):
    def test_model_columns_match_pipeline_columns(self) -> None:
        self.assertEqual(sorted(schemas.MODEL_COLUMNS), sorted(RAW_COLS))
        self.assertEqual(len(schemas.REQUEST_FIELDS), len(schemas.MODEL_COLUMNS))

    def test_synonyms_only_produce_canonical_values(self) -> None:
        canonical = {
            schemas.GENDER: schemas.GENDER_VALUES,
            schemas.MARRIED: schemas.YES_NO_VALUES,
            schemas.SELF_EMPLOYED: schemas.YES_NO_VALUES,
            schemas.EDUCATION: schemas.EDUCATION_VALUES,
            schemas.PROPERTY_AREA: schemas.PROPERTY_AREA_VALUES,
            schemas.CREDIT_HISTORY: (schemas.CREDIT_GOOD, schemas.CREDIT_BAD),
        }
        self.assertEqual(set(canonical), set(schemas.CHOICE_FIELDS))
        for name, allowed in canonical.items():
            self.assertLessEqual(set(CHOICE_SYNONYMS[name].values()), set(allowed), name)

    def test_selection_rule_prefers_lower_std_on_ties(self) -> None:
        base = {"accuracy": 0.8, "precision": 0.8, "recall": 0.8, "f1": 0.8}
        metrics = [
            {**base, "name": "A", "cv_accuracy_mean": 0.8000, "cv_accuracy_std": 0.05},
            {**base, "name": "B", "cv_accuracy_mean": 0.7995, "cv_accuracy_std": 0.01},
            {**base, "name": "C", "cv_accuracy_mean": 0.7900, "cv_accuracy_std": 0.00},
        ]
        self.assertEqual(choose_model(metrics), "B")  # type: ignore[arg-type]


@unittest.skipUnless(HAS_MODEL, SKIP_NO_MODEL)
class SavedModelTests(unittest.TestCase):
    def test_saved_model_is_monotonic(self) -> None:
        pipe = joblib.load(DEFAULT_SETTINGS.model_path)
        sweeps = check_monotonicity(pipe)
        self.assertEqual(len(sweeps), 12)  # 3 profiles x 4 sweeps, all passed

    def test_pickle_references_new_module_path(self) -> None:
        self.assertIn(b"loanwise.ml.features", DEFAULT_SETTINGS.model_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
