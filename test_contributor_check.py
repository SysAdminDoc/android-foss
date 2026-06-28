#!/usr/bin/env python3
"""Offline tests for contributor acceptance checks."""

from __future__ import annotations

import unittest

from catalog_check import AppEntry, StoreLink
from contributor_check import check_entries, check_source_url


class ContributorCheckTests(unittest.TestCase):
    def test_blocked_anti_feature_is_error(self) -> None:
        entry = AppEntry(
            12,
            "Example",
            "https://example.test/source",
            (StoreLink("F-Droid", "https://f-droid.org/packages/org.example", "org.example", 12, "Example"),),
        )
        trust = {
            "Example": {
                "packages": [
                    {
                        "packageId": "org.example",
                        "license": "GPL-3.0-only",
                        "lastUpdated": "2026-06-28",
                        "antiFeatures": ["Tracking"],
                    }
                ]
            }
        }

        findings = check_entries([entry], trust, skip_network=True, timeout=1.0, stale_days=730)

        self.assertEqual(1, len(findings))
        self.assertEqual("ERROR", findings[0].level)

    def test_http_source_is_warning(self) -> None:
        entry = AppEntry(8, "Example", "http://example.test/source", ())

        findings = check_source_url(entry)

        self.assertEqual("WARN", findings[0].level)


if __name__ == "__main__":
    unittest.main()
