"""SQLite-backed store of past predictions (``instance/loanwise.db`` by default).

Each call opens its own short-lived connection, so one repository instance can
be shared safely across request threads; writes are additionally serialised
with a lock to avoid ``database is locked`` errors under the dev server.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

_SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    inputs      TEXT    NOT NULL,
    approved    INTEGER NOT NULL,
    verdict     TEXT    NOT NULL,
    confidence  REAL    NOT NULL,
    result      TEXT
)
"""
_INSERT = (
    "INSERT INTO predictions (created_at, inputs, approved, verdict, confidence, result) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)
_SELECT_RECENT = (
    "SELECT id, created_at, inputs, approved, verdict, confidence "
    "FROM predictions ORDER BY id DESC LIMIT ?"
)
_DELETE_ALL = "DELETE FROM predictions"
_CONNECT_TIMEOUT_SECONDS = 10


class HistoryItem(TypedDict):
    """One row of ``GET /api/history``."""

    id: int
    created_at: str
    inputs: dict[str, Any]
    approved: bool
    verdict: str
    confidence: float


class HistoryRepository:
    """Append-only prediction log with list and clear operations."""

    def __init__(self, path: Path) -> None:
        """Create the database file (and its directory) if needed."""
        self.path = path
        self._write_lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(_SCHEMA)

    def add(
        self,
        inputs: Mapping[str, Any],
        *,
        approved: bool,
        verdict: str,
        confidence: float,
        result: Mapping[str, Any] | None = None,
    ) -> int:
        """Store one prediction and return its new id."""
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = (
            created,
            json.dumps(dict(inputs), ensure_ascii=False),
            int(bool(approved)),
            verdict,
            float(confidence),
            json.dumps(dict(result), ensure_ascii=False) if result else None,
        )
        with self._write_lock, self._connect() as conn:
            cursor = conn.execute(_INSERT, row)
            return int(cursor.lastrowid or 0)

    def list_recent(self, limit: int = 50) -> list[HistoryItem]:
        """Return up to ``limit`` predictions, newest first."""
        with self._connect() as conn:
            rows = conn.execute(_SELECT_RECENT, (int(limit),)).fetchall()
        return [
            HistoryItem(
                id=row["id"],
                created_at=row["created_at"],
                inputs=json.loads(row["inputs"]),
                approved=bool(row["approved"]),
                verdict=row["verdict"],
                confidence=row["confidence"],
            )
            for row in rows
        ]

    def clear(self) -> None:
        """Delete every stored prediction."""
        with self._write_lock, self._connect() as conn:
            conn.execute(_DELETE_ALL)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection that commits on success and always closes."""
        conn = sqlite3.connect(self.path, timeout=_CONNECT_TIMEOUT_SECONDS)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()
