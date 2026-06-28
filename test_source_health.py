#!/usr/bin/env python3
"""Offline tests for source health classification."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from source_health import SourceTarget, classify_github, classify_http


def target(url: str = "https://github.com/example/project") -> SourceTarget:
    return SourceTarget(url=url, names=("Example",), lines=(42,))


class SourceHealthTests(unittest.TestCase):
    def test_github_archived_repository_is_reported(self) -> None:
        data = {
            "html_url": "https://github.com/example/project",
            "archived": True,
            "pushed_at": "2026-01-01T00:00:00Z",
        }
        with patch("source_health.request_json", return_value=(200, "https://api.github.com/repos/example/project", {}, data)):
            result = classify_github(target(), timeout=1.0, stale_days=730)

        self.assertIsNotNone(result)
        self.assertEqual("archived", result.status)

    def test_github_canonical_url_change_is_moved(self) -> None:
        data = {
            "html_url": "https://github.com/new-owner/project",
            "archived": False,
            "pushed_at": "2026-01-01T00:00:00Z",
        }
        with patch("source_health.request_json", return_value=(200, "https://api.github.com/repos/example/project", {}, data)):
            result = classify_github(target(), timeout=1.0, stale_days=730)

        self.assertIsNotNone(result)
        self.assertEqual("moved", result.status)
        self.assertEqual("https://github.com/new-owner/project", result.final_url)

    def test_github_old_push_is_stale(self) -> None:
        pushed_at = datetime.now(timezone.utc) - timedelta(days=731)
        data = {
            "html_url": "https://github.com/example/project",
            "archived": False,
            "pushed_at": pushed_at.isoformat().replace("+00:00", "Z"),
        }
        with patch("source_health.request_json", return_value=(200, "https://api.github.com/repos/example/project", {}, data)):
            result = classify_github(target(), timeout=1.0, stale_days=730)

        self.assertIsNotNone(result)
        self.assertEqual("stale", result.status)

    def test_http_redirect_is_moved(self) -> None:
        with patch("source_health.request_url", return_value=(200, "https://new.example/project", {})):
            result = classify_http(target("https://old.example/project"), timeout=1.0)

        self.assertEqual("moved", result.status)
        self.assertEqual("https://new.example/project", result.final_url)

    def test_http_404_is_missing(self) -> None:
        error = HTTPError("https://old.example/project", 404, "Not Found", {}, None)
        with patch("source_health.request_url", side_effect=error):
            result = classify_http(target("https://old.example/project"), timeout=1.0)

        self.assertEqual("missing", result.status)


if __name__ == "__main__":
    unittest.main()
