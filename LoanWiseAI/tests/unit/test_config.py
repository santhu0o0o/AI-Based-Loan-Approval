"""Settings are read from LOANWISE_* environment variables with safe defaults."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from loanwise.api import create_app
from loanwise.config import DEFAULT_CORS_ORIGINS, PROJECT_ROOT, ConfigError, Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_point_inside_project(self) -> None:
        s = Settings.from_env({})
        self.assertEqual(s.model_path, PROJECT_ROOT / "artifacts/models/loan_model.pkl")
        self.assertEqual(s.model_info_path, PROJECT_ROOT / "artifacts/models/model_info.json")
        self.assertEqual(s.database_path, PROJECT_ROOT / "instance/loanwise.db")
        self.assertEqual(s.sample_data_path, PROJECT_ROOT / "data/raw/test.csv")
        self.assertEqual(s.frontend_dist, PROJECT_ROOT / "frontend/dist")
        self.assertEqual((s.host, s.port, s.debug), ("0.0.0.0", 5000, False))
        self.assertEqual(s.max_request_bytes, 32 * 1024)
        self.assertEqual(s.cors_origins, DEFAULT_CORS_ORIGINS)

    def test_root_and_relative_paths(self) -> None:
        s = Settings.from_env(
            {
                "LOANWISE_ROOT": "/srv/app",
                "LOANWISE_DATABASE_PATH": "db/x.db",
                "LOANWISE_MODEL_PATH": "/models/m.pkl",
            }
        )
        self.assertEqual(s.database_path, Path("/srv/app/db/x.db"))
        self.assertEqual(s.model_path, Path("/models/m.pkl"))
        self.assertEqual(s.train_data_path, Path("/srv/app/data/raw/loan.csv"))

    def test_scalar_overrides(self) -> None:
        s = Settings.from_env(
            {
                "LOANWISE_HOST": "127.0.0.1",
                "LOANWISE_PORT": "8080",
                "LOANWISE_DEBUG": "yes",
                "LOANWISE_MAX_REQUEST_BYTES": "1024",
                "LOANWISE_CORS_ORIGINS": " https://a.example , ,https://b.example",
                "LOANWISE_LOG_LEVEL": "debug",
                "LOANWISE_LOG_FORMAT": "JSON",
            }
        )
        self.assertEqual((s.host, s.port, s.debug), ("127.0.0.1", 8080, True))
        self.assertEqual(s.max_request_bytes, 1024)
        self.assertEqual(s.cors_origins, ("https://a.example", "https://b.example"))
        self.assertEqual((s.log_level, s.log_format), ("DEBUG", "json"))

    def test_port_falls_back_to_platform_port(self) -> None:
        self.assertEqual(Settings.from_env({"PORT": "7000"}).port, 7000)
        self.assertEqual(Settings.from_env({"PORT": "7000", "LOANWISE_PORT": "7001"}).port, 7001)

    def test_invalid_values_raise(self) -> None:
        for env in (
            {"LOANWISE_PORT": "abc"},
            {"LOANWISE_PORT": "-1"},
            {"LOANWISE_DEBUG": "maybe"},
            {"LOANWISE_LOG_FORMAT": "xml"},
        ):
            with self.assertRaises(ConfigError, msg=env):
                Settings.from_env(env)

    def test_max_request_bytes_applied_to_app(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(
                Settings.from_env(
                    {"LOANWISE_MAX_REQUEST_BYTES": "2048", "LOANWISE_DATABASE_PATH": f"{tmp}/h.db"}
                )
            )
            self.assertEqual(app.config["MAX_CONTENT_LENGTH"], 2048)
            response = app.test_client().post(
                "/api/predict", data="x" * 4096, content_type="application/json"
            )
            self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
