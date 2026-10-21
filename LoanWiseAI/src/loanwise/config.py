"""Runtime configuration, read once from ``LOANWISE_*`` environment variables.

Every path defaults to a location inside the project root, so a fresh checkout
works with no configuration at all. The project root is detected from this
file's location (``<root>/src/loanwise/config.py``); set ``LOANWISE_ROOT`` when
the package is installed somewhere else (for example inside a container).

Environment variables (all optional):

==========================  ================================  ================================
Variable                    Meaning                           Default
==========================  ================================  ================================
LOANWISE_ROOT               base for relative defaults        project root
LOANWISE_MODEL_PATH         trained pipeline (joblib)         artifacts/models/loan_model.pkl
LOANWISE_MODEL_INFO_PATH    report for /api/model-info        artifacts/models/model_info.json
LOANWISE_DATABASE_PATH      SQLite prediction history         instance/loanwise.db
LOANWISE_TRAIN_DATA_PATH    labelled training CSV             data/raw/loan.csv
LOANWISE_SAMPLE_DATA_PATH   demo CSV for /api/sample          data/raw/test.csv
LOANWISE_EDA_DIR            EDA charts written by training    artifacts/reports/eda
LOANWISE_FRONTEND_DIST      built React app served at /       frontend/dist
LOANWISE_HOST               dev-server bind address           0.0.0.0
LOANWISE_PORT               dev-server port (or ``PORT``)     5000
LOANWISE_DEBUG              Flask debug (dev server only)     false
LOANWISE_MAX_REQUEST_BYTES  largest accepted request body     32768
LOANWISE_CORS_ORIGINS       allowed origins, scheme://host (CSV) localhost, 127.0.0.1
LOANWISE_LOG_LEVEL          root log level                    INFO
LOANWISE_LOG_FORMAT         ``text`` or ``json``              text
==========================  ================================  ================================
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGINS: tuple[str, ...] = (
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
)

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off", ""})
_LOG_FORMATS = frozenset({"text", "json"})


class ConfigError(ValueError):
    """Raised when an environment variable holds a value that cannot be used."""


@dataclass(frozen=True)
class Settings:
    """Immutable application settings.

    Build with :meth:`Settings.from_env`; derive variants (for tests) with
    :func:`dataclasses.replace`.
    """

    model_path: Path
    model_info_path: Path
    database_path: Path
    train_data_path: Path
    sample_data_path: Path
    eda_dir: Path
    frontend_dist: Path
    host: str = "0.0.0.0"  # noqa: S104 - dev server is expected to be reachable in containers
    port: int = 5000
    debug: bool = False
    max_request_bytes: int = 32 * 1024  # a loan form is tiny; refuse anything big
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS
    log_level: str = "INFO"
    log_format: str = "text"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        """Create settings from ``env`` (defaults to :data:`os.environ`).

        Raises:
            ConfigError: if a numeric, boolean or enumerated variable is invalid.
        """
        env = os.environ if env is None else env
        root = Path(env.get("LOANWISE_ROOT") or PROJECT_ROOT).resolve()

        def path(name: str, default: str) -> Path:
            value = Path(env.get(f"LOANWISE_{name}") or default)
            return value if value.is_absolute() else root / value

        return cls(
            model_path=path("MODEL_PATH", "artifacts/models/loan_model.pkl"),
            model_info_path=path("MODEL_INFO_PATH", "artifacts/models/model_info.json"),
            database_path=path("DATABASE_PATH", "instance/loanwise.db"),
            train_data_path=path("TRAIN_DATA_PATH", "data/raw/loan.csv"),
            sample_data_path=path("SAMPLE_DATA_PATH", "data/raw/test.csv"),
            eda_dir=path("EDA_DIR", "artifacts/reports/eda"),
            frontend_dist=path("FRONTEND_DIST", "frontend/dist"),
            host=env.get("LOANWISE_HOST") or "0.0.0.0",  # noqa: S104
            port=_int(env, "LOANWISE_PORT", fallback=_int(env, "PORT", fallback=5000)),
            debug=_bool(env, "LOANWISE_DEBUG", fallback=False),
            max_request_bytes=_int(env, "LOANWISE_MAX_REQUEST_BYTES", fallback=32 * 1024),
            cors_origins=_csv(env, "LOANWISE_CORS_ORIGINS", fallback=DEFAULT_CORS_ORIGINS),
            log_level=(env.get("LOANWISE_LOG_LEVEL") or "INFO").upper(),
            log_format=_choice(env, "LOANWISE_LOG_FORMAT", _LOG_FORMATS, fallback="text"),
        )


def _int(env: Mapping[str, str], name: str, *, fallback: int) -> int:
    """Read a positive integer variable, or ``fallback`` when unset/blank."""
    raw = env.get(name, "").strip()
    if not raw:
        return fallback
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from None
    if value <= 0:
        raise ConfigError(f"{name} must be positive, got {value}")
    return value


def _bool(env: Mapping[str, str], name: str, *, fallback: bool) -> bool:
    """Read a boolean variable (``1/0``, ``true/false``, ``yes/no``, ``on/off``)."""
    if name not in env:
        return fallback
    raw = env[name].strip().lower()
    if raw in _TRUE_VALUES:
        return True
    if raw in _FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be a boolean (true/false), got {env[name]!r}")


def _csv(env: Mapping[str, str], name: str, *, fallback: tuple[str, ...]) -> tuple[str, ...]:
    """Read a comma-separated list variable, dropping blank items."""
    raw = env.get(name)
    if raw is None or not raw.strip():
        return fallback
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _choice(env: Mapping[str, str], name: str, allowed: frozenset[str], *, fallback: str) -> str:
    """Read a variable restricted to ``allowed`` values (case-insensitive)."""
    raw = (env.get(name) or fallback).strip().lower()
    if raw not in allowed:
        raise ConfigError(f"{name} must be one of {sorted(allowed)}, got {raw!r}")
    return raw
