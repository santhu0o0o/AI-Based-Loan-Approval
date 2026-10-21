"""LoanWise AI test suite (stdlib ``unittest``; also collected by pytest).

Run from the project root::

    python3 -m unittest discover -s tests -t .

Importing this package puts ``src/`` on ``sys.path`` so the suite also runs
without ``pip install -e .``, and silences the ``loanwise`` loggers: expected
failures are logged by the code under test (``assertLogs`` still works because
it attaches its own handler).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_LOGGER = logging.getLogger("loanwise")
_LOGGER.addHandler(logging.NullHandler())
_LOGGER.propagate = False
