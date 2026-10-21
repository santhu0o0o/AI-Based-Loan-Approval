#!/usr/bin/env python3
"""Run the development server: ``python3 scripts/run_server.py`` (same as ``loanwise-serve``)."""

from __future__ import annotations

from _bootstrap import ensure_src_on_path

ensure_src_on_path()

from loanwise.api.dev_server import main  # noqa: E402

if __name__ == "__main__":
    main()
