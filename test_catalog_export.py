#!/usr/bin/env python3
"""Offline tests for catalog JSON export."""

from __future__ import annotations

import unittest

from catalog_export import export_catalog


class CatalogExportTests(unittest.TestCase):
    def test_exports_category_source_host_and_package_ids(self) -> None:
        lines = [
            "# Android FOSS\n",
            "## - Apps -\n",
            "### - Browser\n",
            "* [**Example**](https://github.com/example/app) <sup>**[[F-Droid](https://f-droid.org/packages/org.example.app)]**</sup>\n",
        ]

        catalog = export_catalog(lines)
        entry = catalog["entries"][0]

        self.assertEqual(1, catalog["entryCount"])
        self.assertEqual("Example", entry["name"])
        self.assertEqual("Browser", entry["category"])
        self.assertEqual("github.com", entry["sourceHost"])
        self.assertEqual("org.example.app", entry["storeLinks"][0]["packageId"])


if __name__ == "__main__":
    unittest.main()
