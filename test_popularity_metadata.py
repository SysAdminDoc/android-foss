#!/usr/bin/env python3
"""Offline tests for popularity metadata helpers."""

from __future__ import annotations

import unittest

from popularity_metadata import date_only, github_repo


class PopularityMetadataTests(unittest.TestCase):
    def test_github_repo_extracts_owner_and_name(self) -> None:
        repo = github_repo("https://github.com/example/project.git")

        self.assertIsNotNone(repo)
        self.assertEqual("example/project", repo.api_name)

    def test_date_only_normalizes_github_timestamp(self) -> None:
        self.assertEqual("2026-06-28", date_only("2026-06-28T12:34:56Z"))


if __name__ == "__main__":
    unittest.main()
