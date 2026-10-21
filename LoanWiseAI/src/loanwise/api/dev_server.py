"""Development server entry point (``loanwise-serve``).

For production, run ``gunicorn wsgi:app`` instead (see the Dockerfile).
"""

from __future__ import annotations

from loanwise.api import create_app
from loanwise.config import Settings
from loanwise.logging_config import configure_logging


def main() -> None:
    """Start Flask's built-in server using ``LOANWISE_*`` settings."""
    settings = Settings.from_env()
    configure_logging(settings.log_level, settings.log_format)
    create_app(settings).run(host=settings.host, port=settings.port, debug=settings.debug)


if __name__ == "__main__":
    main()
