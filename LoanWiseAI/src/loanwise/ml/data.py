"""Loading the labelled training data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from loanwise.domain.schemas import TARGET_APPROVED, TARGET_COLUMN
from loanwise.ml.features import RAW_COLS


@dataclass(frozen=True)
class TrainingData:
    """The raw table plus the model inputs ``X`` and binary target ``y`` (1 = approved)."""

    raw: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series

    @property
    def summary(self) -> dict[str, int]:
        """Row counts recorded in ``model_info.json``."""
        return {
            "rows": len(self.y),
            "approved": int(self.y.sum()),
            "rejected": int((self.y == 0).sum()),
        }


def load_training_data(path: Path) -> TrainingData:
    """Read the labelled CSV; missing values are left for the pipeline to impute."""
    raw = pd.read_csv(path)
    X = raw[RAW_COLS].copy()
    y = (raw[TARGET_COLUMN] == TARGET_APPROVED).astype(int)
    return TrainingData(raw=raw, X=X, y=y)
