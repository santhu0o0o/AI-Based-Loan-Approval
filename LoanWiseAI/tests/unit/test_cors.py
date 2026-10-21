"""Unit tests for the CORS origin allow-list."""

from __future__ import annotations

import unittest

from loanwise.api import is_allowed_origin
from loanwise.config import DEFAULT_CORS_ORIGINS


class AllowedOriginTests(unittest.TestCase):
    """Only exact scheme + host matches are allowed; any port is fine."""

    def test_local_dev_origins_allowed(self) -> None:
        for origin in ("http://localhost:5173", "http://127.0.0.1:8000", "http://localhost"):
            with self.subTest(origin=origin):
                self.assertTrue(is_allowed_origin(origin, DEFAULT_CORS_ORIGINS))

    def test_lookalike_and_foreign_origins_rejected(self) -> None:
        for origin in (
            "http://localhost.evil.com",
            "http://127.0.0.1.evil.com:5173",
            "https://evil.com",
            "http://localhost:abc",
            "localhost:5173",
            "",
            "null",
        ):
            with self.subTest(origin=origin):
                self.assertFalse(is_allowed_origin(origin, DEFAULT_CORS_ORIGINS))

    def test_empty_allow_list_rejects_everything(self) -> None:
        self.assertFalse(is_allowed_origin("http://localhost:5173", ()))


if __name__ == "__main__":
    unittest.main()
