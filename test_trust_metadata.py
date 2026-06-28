#!/usr/bin/env python3
"""Offline tests for trust metadata generation."""

from __future__ import annotations

import unittest

from catalog_check import AppEntry, StoreLink
from trust_metadata import RepoIndex, build_catalog, normalize_index


class TrustMetadataTests(unittest.TestCase):
    def test_v1_index_extracts_anti_features_and_sensitive_permissions(self) -> None:
        data = {
            "repo": {"timestamp": 1234},
            "apps": [
                {
                    "packageName": "org.example.app",
                    "license": "GPL-3.0-only",
                    "lastUpdated": 1780528236000,
                    "antiFeatures": ["NonFreeNet"],
                    "sourceCode": "https://example.test/source",
                }
            ],
            "packages": [
                {
                    "packageName": "org.example.app",
                    "versionCode": 5,
                    "src": {"name": "org.example.app_5_src.tar.gz"},
                    "manifest": {
                        "usesPermission": [
                            {"name": "android.permission.INTERNET"},
                            {"name": "android.permission.CAMERA"},
                        ]
                    },
                }
            ],
        }
        fdroid = normalize_index("F-Droid", "fdroid.json", data)
        izzy = RepoIndex("IzzyOnDroid", "izzy.json", None, {}, {})
        entry = AppEntry(
            7,
            "Example",
            "https://example.test/source",
            (StoreLink("F-Droid", "https://f-droid.org/packages/org.example.app", "org.example.app", 7, "Example"),),
        )

        catalog = build_catalog([entry], fdroid, izzy, verify=False, timeout=1.0)
        package = catalog["entries"]["Example"]["packages"][0]

        self.assertEqual(["NonFreeNet"], package["antiFeatures"])
        self.assertEqual(["android.permission.CAMERA"], package["sensitivePermissions"])
        self.assertEqual("2026-06-03", package["lastUpdated"])
        self.assertTrue(package["sourceArchive"])

    def test_v2_index_metadata_is_supported(self) -> None:
        data = {
            "repo": {"timestamp": 5678},
            "packages": {
                "org.example.app": {
                    "metadata": {
                        "license": "Apache-2.0",
                        "lastUpdated": 1780528236000,
                        "sourceCode": "https://example.test/source",
                    },
                    "versions": {
                        "abc": {
                            "manifest": {
                                "versionCode": 10,
                                "usesPermission": [{"name": "android.permission.RECORD_AUDIO"}],
                            },
                            "antiFeatures": {"Tracking": {}},
                        }
                    },
                }
            },
        }
        repo = normalize_index("F-Droid", "fdroid.json", data)

        self.assertIn("org.example.app", repo.apps)
        self.assertEqual(1, len(repo.versions["org.example.app"]))


if __name__ == "__main__":
    unittest.main()
