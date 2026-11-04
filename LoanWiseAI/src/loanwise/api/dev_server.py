"""Development server entry point (``loanwise-serve``).

For production, run ``gunicorn wsgi:app`` instead (see the Dockerfile).
"""

from __future__ import annotations

import logging
import socket

from loanwise.api import create_app
from loanwise.config import Settings
from loanwise.logging_config import configure_logging

log = logging.getLogger(__name__)


def _is_port_available(host: str, port: int) -> bool:
    """Check if the address can be bound."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.close()
        return True
    except OSError:
        return False


def _find_free_port(host: str, preferred: int, candidates: tuple[int, ...] = (8000, 8080, 5001, 8081)) -> int:
    """Return preferred port if free, or first free candidate."""
    if _is_port_available(host, preferred):
        return preferred
    for p in candidates:
        if _is_port_available(host, p):
            return p
    return preferred


def main() -> None:
    """Start Flask's built-in server using ``LOANWISE_*`` settings."""
    settings = Settings.from_env()
    configure_logging(settings.log_level, settings.log_format)

    host = settings.host
    port = settings.port
    if not _is_port_available(host, port):
        fallback_port = _find_free_port(host, port)
        if fallback_port != port:
            log.warning(
                "Port %d on %s is in use (often AirPlay Receiver on macOS). Automatically falling back to port %d.",
                port,
                host,
                fallback_port,
            )
            port = fallback_port

    create_app(settings).run(host=host, port=port, debug=settings.debug)


if __name__ == "__main__":
    main()
