"""WSGI entry point for production servers: ``gunicorn wsgi:app``."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))  # allow running from a checkout without `pip install`

from loanwise.api import create_app  # noqa: E402
from loanwise.config import Settings  # noqa: E402
from loanwise.logging_config import configure_logging  # noqa: E402

settings = Settings.from_env()
configure_logging(settings.log_level, settings.log_format)
app = create_app(settings)
