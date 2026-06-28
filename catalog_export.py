#!/usr/bin/env python3
"""Export the README catalog to deterministic machine-readable JSON."""

from __future__ import annotations

from argparse import ArgumentParser
import json
import re
from pathlib import Path
import sys
from urllib.parse import urlparse

from catalog_check import README, AppEntry, parse_entries, validate_duplicate_packages


OUTPUT = Path("catalog.json")
HEADING_RE = re.compile(r"^(?P<level>#{2,3})\s+(?P<text>.+?)\s*$")


def clean_heading(text: str) -> str:
    return text.replace("&amp;", "&").strip(" -–•\t")


def source_host(url: str) -> str:
    return urlparse(url).netloc.lower()


def entry_to_json(entry: AppEntry, category: str) -> dict[str, object]:
    return {
        "line": entry.line_number,
        "name": entry.name,
        "category": category,
        "sourceUrl": entry.source_url,
        "sourceHost": source_host(entry.source_url),
        "storeLinks": [
            {
                "store": link.store,
                "url": link.url,
                "packageId": link.package_id,
            }
            for link in entry.store_links
        ],
    }


def export_catalog(lines: list[str]) -> dict[str, object]:
    entries, errors = parse_entries(lines)
    validate_duplicate_packages(entries, errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")

    by_line = {entry.line_number: entry for entry in entries}
    exported: list[dict[str, object]] = []
    section = "Catalog"
    category = section

    for line_number, line in enumerate(lines, start=1):
        heading = HEADING_RE.match(line.strip())
        if heading:
            text = clean_heading(heading.group("text"))
            if heading.group("level") == "##":
                section = text
                category = section
            else:
                category = text

        entry = by_line.get(line_number)
        if entry:
            exported.append(entry_to_json(entry, category))

    return {
        "schemaVersion": 1,
        "source": str(README),
        "entryCount": len(exported),
        "entries": exported,
    }


def main() -> int:
    parser = ArgumentParser(description="Export README.md catalog entries to catalog.json.")
    parser.add_argument("--output", default=str(OUTPUT), help="JSON output path")
    args = parser.parse_args()

    catalog = export_catalog(README.read_text(encoding="utf-8").splitlines(keepends=True))
    output = Path(args.output)
    output.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output}: {catalog['entryCount']} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
