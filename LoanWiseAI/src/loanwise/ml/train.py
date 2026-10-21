"""Training entry point (``loanwise-train`` / ``python scripts/train_model.py``).

Steps:

1. Load the labelled CSV, print an EDA summary and save charts.
2. Tune Logistic Regression, Decision Tree and Random Forest pipelines with
   5-fold CV on a stratified 80% split; report metrics on the 20% hold-out.
3. Choose the winner by :data:`~loanwise.ml.evaluation.SELECTION_RULE` and refit
   it on all labelled rows.
4. Refuse to save unless every model passes the monotonicity check.
5. Save the pipeline and ``model_info.json``, then load the saved file in a
   fresh interpreter as a final sanity check.

The demo CSV has no labels; it is only used for that sanity check.
This module is a CLI, so it prints its report to stdout.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

import loanwise
from loanwise.config import Settings
from loanwise.logging_config import configure_logging
from loanwise.ml.data import TrainingData, load_training_data
from loanwise.ml.eda import describe_dataset, save_eda_charts
from loanwise.ml.evaluation import (
    SELECTION_RULE,
    EvaluationReport,
    check_monotonicity,
    choose_model,
    evaluate_models,
    feature_importance,
)

RULE = "=" * 70


def main() -> None:
    """Run the full training workflow using ``LOANWISE_*`` settings."""
    settings = Settings.from_env()
    configure_logging(settings.log_level, settings.log_format)
    data = load_training_data(settings.train_data_path)
    _run_eda(data, settings.eda_dir)

    report = evaluate_models(data.X, data.y)
    _print_comparison(report)
    chosen = choose_model(report.metrics)
    _say(f"\nChosen model: {chosen}\n  Rule: {SELECTION_RULE}")

    final_pipe = report.fitted[chosen].pipeline
    final_pipe.fit(data.X, data.y)  # refit the tuned pipeline on all labelled rows
    _verify_monotonicity(final_pipe, chosen, report)

    _save_model(final_pipe, settings.model_path)
    _save_model_info(final_pipe, chosen, report, data, settings.model_info_path)
    _sanity_check(settings)


def _run_eda(data: TrainingData, eda_dir: Path) -> None:
    """Print the dataset summary and write the charts."""
    _banner("EXPLORATORY DATA ANALYSIS")
    _say(describe_dataset(data.raw))
    charts = save_eda_charts(data.raw, eda_dir)
    _say(f"\nSaved {len(charts)} EDA charts to {_display(eda_dir)}/")


def _print_comparison(report: EvaluationReport) -> None:
    """Print the metrics table, tuned parameters and the always-approve baseline."""
    _banner("MODEL COMPARISON (test = 20% hold-out, CV = 5-fold on the 80% train)", lead="\n")
    _say(pd.DataFrame(report.metrics).set_index("name").to_string())
    for name, fitted in report.fitted.items():
        _say(f"  {name} best params: {fitted.best_params}")
    _say(f"\n  Baseline (always 'approved') test accuracy: {report.baseline_accuracy:.4f}")


def _verify_monotonicity(final_pipe: Any, chosen: str, report: EvaluationReport) -> None:
    """Check the chosen model, then the others for a fair comparison; raises on failure."""
    _say("\nMonotonicity check (chosen model, refit on all data):")
    _print_sweeps(final_pipe)
    for name, fitted in report.fitted.items():
        if name != chosen:
            _say(f"  [{name} (train split)]")
            _print_sweeps(fitted.pipeline)


def _print_sweeps(pipe: Any) -> None:
    """Run :func:`check_monotonicity` on ``pipe`` and print each passed sweep."""
    for sweep in check_monotonicity(pipe):
        _say(
            f"  OK  profile {sweep.profile}: {sweep.label:<22} "
            f"P {sweep.p_start:.3f} -> {sweep.p_end:.3f}"
        )
    _say("  Monotonicity check PASSED")


def _save_model(pipe: Any, path: Path) -> None:
    """Persist the fitted pipeline with joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, path)
    _say(f"\nSaved model to {_display(path)}")


def _save_model_info(
    pipe: Any, chosen: str, report: EvaluationReport, data: TrainingData, path: Path
) -> None:
    """Write the training report consumed by ``GET /api/model-info``."""
    importance, method = feature_importance(pipe)
    _say("\nTop features:")
    for item in importance:
        _say(f"  {item['feature']:<28} {item['importance']:.3f}")
    info = {
        "chosen_model": chosen,
        "selection_metric": SELECTION_RULE,
        "models": report.metrics,
        "feature_importance": importance,
        "importance_method": method,
        "dataset": data.summary,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    _say(f"Saved model info to {_display(path)}")


def _sanity_check(settings: Settings) -> None:
    """Load the saved model in a fresh interpreter (as the API would) and score samples."""
    _banner("SANITY CHECK (fresh Python process loading the saved model)", lead="\n")
    package_parent = Path(loanwise.__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            filter(None, [str(package_parent), os.environ.get("PYTHONPATH")])
        ),
    }
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        [
            sys.executable,
            "-m",
            "loanwise.ml.sanity",
            str(settings.model_path),
            str(settings.sample_data_path),
        ],
        check=True,
        env=env,
    )


def _banner(title: str, *, lead: str = "") -> None:
    """Print a section heading."""
    _say(f"{lead}{RULE}\n{title}\n{RULE}")


def _say(text: str) -> None:
    """Print one block of the training report."""
    print(text)


def _display(path: Path) -> str:
    """Show ``path`` relative to the working directory when possible."""
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
