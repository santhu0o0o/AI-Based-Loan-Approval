"""Make ``src/`` importable when the package has not been ``pip install``-ed."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"


def ensure_src_on_path() -> None:
    """Prepend ``<repo>/src`` to :data:`sys.path` if it is not already there."""
    if SRC_DIR.is_dir() and str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
