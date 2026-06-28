#!/usr/bin/env python3
"""Offline tests for catalog identity checks."""

from __future__ import annotations

import unittest

from catalog_check import AppEntry, StoreLink
from identity_check import duplicate_findings, duplicate_package_findings, likely_fork_findings


class IdentityCheckTests(unittest.TestCase):
    def test_duplicate_source_is_reported(self) -> None:
        entries = [
            AppEntry(1, "One", "https://github.com/example/app", ()),
            AppEntry(2, "Two", "https://github.com/example/app", ()),
        ]

        findings = duplicate_findings(entries)

        self.assertEqual("DUPLICATE_SOURCE", findings[0].classification)

    def test_duplicate_package_is_reported(self) -> None:
        link = StoreLink("F-Droid", "https://f-droid.org/packages/org.example", "org.example", 1, "One")
        entries = [
            AppEntry(1, "One", "https://example.test/one", (link,)),
            AppEntry(2, "Two", "https://example.test/two", (link,)),
        ]

        findings = duplicate_package_findings(entries)

        self.assertEqual("DUPLICATE_PACKAGE", findings[0].classification)

    def test_likely_fork_repo_slug_is_reported(self) -> None:
        entries = [
            AppEntry(1, "One", "https://github.com/owner-one/wallet", ()),
            AppEntry(2, "Two", "https://github.com/owner-two/wallet", ()),
        ]

        findings = likely_fork_findings(entries)

        self.assertTrue(any(finding.classification == "LIKELY_FORK_REPO_SLUG" for finding in findings))


if __name__ == "__main__":
    unittest.main()
