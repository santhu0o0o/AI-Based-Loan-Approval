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


def _someone_listening(port: int) -> bool:
    """True if anything accepts connections on loopback (IPv4 or IPv6) at ``port``.

    Catches listeners a plain bind() check misses, e.g. macOS AirPlay Receiver
    on ``*:5000``, which coexists with a 127.0.0.1 bind under SO_REUSEADDR.
    """
    for family, addr in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex((addr, port)) == 0:
                    return True
        except OSError:
            continue
    return False


def _is_port_available(host: str, port: int) -> bool:
    """Check if the address can be bound and nothing else is listening on the port."""
    if _someone_listening(port):
        return False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


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
