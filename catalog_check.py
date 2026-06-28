#!/usr/bin/env python3
"""Validate the Android FOSS README catalog."""

from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path


README = Path("README.md")
APP_RE = re.compile(
    r"^(?P<indent>\s*)\* \[\*\*(?P<name>.+?)\*\*\]\((?P<source>[^)\s]+)\)(?P<rest>.*)$"
)
STORE_RE = re.compile(r"\[\[(?P<store>F-Droid|IzzyOnDroid)\]\((?P<url>[^)\s]+)\)\]")
FDROID_PREFIX = "https://f-droid.org/packages/"
IZZY_PREFIX = "https://apt.izzysoft.de/packages/"
PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class StoreLink:
    store: str
    url: str
    package_id: str
    line_number: int
    entry_name: str


@dataclass(frozen=True)
class AppEntry:
    line_number: int
    name: str
    source_url: str
    store_links: tuple[StoreLink, ...]


def package_id_for(store: str, url: str) -> str | None:
    prefix = FDROID_PREFIX if store == "F-Droid" else IZZY_PREFIX
    if not url.startswith(prefix):
        return None
    package_id = url.removeprefix(prefix).rstrip("/")
    if "/" in package_id:
        return None
    return package_id


def parse_entries(lines: list[str]) -> tuple[list[AppEntry], list[str]]:
    entries: list[AppEntry] = []
    errors: list[str] = []

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        if not re.match(r"^\s*\* \[\*\*", line):
            continue

        match = APP_RE.match(line)
        if not match:
            errors.append(f"README.md:{line_number}: malformed app entry")
            continue

        rest = match.group("rest")
        if rest.count("<sup>") != rest.count("</sup>"):
            errors.append(f"README.md:{line_number}: unmatched <sup> store badge markup")

        store_links: list[StoreLink] = []
        stores_in_order: list[str] = []
        for store_match in STORE_RE.finditer(rest):
            store = store_match.group("store")
            url = store_match.group("url")
            stores_in_order.append(store)
            package_id = package_id_for(store, url)
            if package_id is None:
                expected = FDROID_PREFIX if store == "F-Droid" else IZZY_PREFIX
                errors.append(
                    f"README.md:{line_number}: invalid {store} URL; expected {expected}<package-id>"
                )
                package_id = ""
            elif not PACKAGE_RE.fullmatch(package_id):
                errors.append(f"README.md:{line_number}: invalid {store} package id '{package_id}'")
            store_links.append(StoreLink(store, url, package_id, line_number, match.group("name").strip()))

        if "IzzyOnDroid" in stores_in_order and "F-Droid" in stores_in_order:
            if stores_in_order.index("IzzyOnDroid") < stores_in_order.index("F-Droid"):
                errors.append(f"README.md:{line_number}: F-Droid store link must appear before IzzyOnDroid")

        entries.append(
            AppEntry(
                line_number=line_number,
                name=match.group("name").strip(),
                source_url=match.group("source").rstrip("/"),
                store_links=tuple(store_links),
            )
        )

    return entries, errors


def validate_duplicate_packages(entries: list[AppEntry], errors: list[str]) -> None:
    packages: dict[str, StoreLink] = {}

    for entry in entries:
        for store_link in entry.store_links:
            if not store_link.package_id:
                continue
            key = store_link.package_id.casefold()
            previous = packages.get(key)
            if previous is None:
                packages[key] = store_link
                continue
            if previous.line_number == store_link.line_number:
                continue
            errors.append(
                f"README.md:{store_link.line_number}: duplicate package id '{store_link.package_id}' "
                f"also used by '{previous.entry_name}' on line {previous.line_number}"
            )


def main() -> int:
    if not README.exists():
        print("README.md: missing catalog source", file=sys.stderr)
        return 1

    lines = README.read_text(encoding="utf-8").splitlines(keepends=True)
    entries, errors = parse_entries(lines)
    validate_duplicate_packages(entries, errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"catalog check failed: {len(errors)} issue(s)", file=sys.stderr)
        return 1

    store_count = sum(len(entry.store_links) for entry in entries)
    print(f"catalog check passed: {len(entries)} entries, {store_count} store links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
