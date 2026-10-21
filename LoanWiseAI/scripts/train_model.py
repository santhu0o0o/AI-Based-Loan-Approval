#!/usr/bin/env python3
"""Train the loan model: ``python3 scripts/train_model.py`` (same as ``loanwise-train``)."""

from __future__ import annotations

from _bootstrap import ensure_src_on_path

ensure_src_on_path()

from loanwise.ml.train import main  # noqa: E402

if __name__ == "__main__":
    main()
