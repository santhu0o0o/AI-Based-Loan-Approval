"""Exploratory data analysis: a text summary and four PNG charts."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import matplotlib

matplotlib.use("Agg")  # headless: never needs a display

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from loanwise.domain.schemas import TARGET_APPROVED, TARGET_COLUMN

GROUP_COLUMNS: Final = ["Credit_History", "Property_Area", "Education", "Married"]
APPROVED_COLOR: Final = "#2a9d8f"
REJECTED_COLOR: Final = "#e76f51"
GROUP_COLOR: Final = "#264653"
MISSING_COLOR: Final = "#e9c46a"
DPI: Final = 120


def describe_dataset(df: pd.DataFrame) -> str:
    """Return a printable summary: shape, missing values, class balance, group approval rates."""
    approved = _approved(df)
    missing = df.isna().sum()
    counts = df[TARGET_COLUMN].value_counts()
    n = len(df)
    lines = [
        f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
        "",
        "Missing values:",
        missing[missing > 0].to_string(),
        "",
        f"Class balance: Approved (Y) = {counts['Y']} ({counts['Y'] / n:.1%}), "
        f"Rejected (N) = {counts['N']} ({counts['N'] / n:.1%})",
    ]
    for col in GROUP_COLUMNS:
        rate = approved.groupby(df[col].fillna("Missing")).agg(["mean", "count"])
        rate.columns = ["approval_rate", "rows"]
        lines += ["", f"Approval rate by {col}:", rate.round(3).to_string()]
    return "\n".join(lines)


def save_eda_charts(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    """Write the EDA charts into ``out_dir`` and return their paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "class_balance.png": _class_balance_chart(df),
        "approval_rate_by_group.png": _group_rate_chart(df),
        "income_distribution.png": _income_chart(df),
        "missing_values.png": _missing_chart(df),
    }
    paths = []
    for filename, fig in charts.items():
        path = out_dir / filename
        fig.tight_layout()
        fig.savefig(path, dpi=DPI)
        plt.close(fig)
        paths.append(path)
    return paths


def _approved(df: pd.DataFrame) -> pd.Series:
    """1 for approved rows, 0 otherwise."""
    return (df[TARGET_COLUMN] == TARGET_APPROVED).astype(int)


def _class_balance_chart(df: pd.DataFrame) -> Figure:
    """Bar chart of approved vs rejected applications."""
    counts = df[TARGET_COLUMN].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(
        ["Approved", "Rejected"], [counts["Y"], counts["N"]], color=[APPROVED_COLOR, REJECTED_COLOR]
    )
    ax.set_title("Loan outcomes in the dataset")
    ax.set_ylabel("Number of applications")
    return fig


def _group_rate_chart(df: pd.DataFrame) -> Figure:
    """Approval rate for each value of the key categorical columns."""
    approved = _approved(df)
    fig, axes = plt.subplots(1, len(GROUP_COLUMNS), figsize=(14, 4), sharey=True)
    for ax, col in zip(axes, GROUP_COLUMNS, strict=True):
        rate = approved.groupby(df[col].fillna("Missing")).mean()
        ax.bar(rate.index.astype(str), rate.values, color=GROUP_COLOR)
        ax.set_title(col.replace("_", " "))
        ax.set_ylim(0, 1)
        ax.tick_params(axis="x", rotation=20)
    axes[0].set_ylabel("Approval rate")
    fig.suptitle("Approval rate by applicant group")
    return fig


def _income_chart(df: pd.DataFrame) -> Figure:
    """Log-scale histogram of total income, split by outcome."""
    approved = _approved(df)
    total_income = df["ApplicantIncome"] + df["CoapplicantIncome"]
    low, high = np.log10(max(total_income.min(), 1)), np.log10(total_income.max())
    bins = np.logspace(low, high, 30).tolist()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(
        total_income[approved == 1], bins=bins, alpha=0.6, label="Approved", color=APPROVED_COLOR
    )
    ax.hist(
        total_income[approved == 0], bins=bins, alpha=0.6, label="Rejected", color=REJECTED_COLOR
    )
    ax.set_xscale("log")
    ax.set_xlabel("Total monthly income (₹, log scale)")
    ax.set_ylabel("Applications")
    ax.set_title("Total income by outcome")
    ax.legend()
    return fig


def _missing_chart(df: pd.DataFrame) -> Figure:
    """Horizontal bars of missing-value counts per column."""
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(missing.index, missing.values, color=MISSING_COLOR)
    ax.set_xlabel("Missing values")
    ax.set_title("Missing values per column")
    return fig
