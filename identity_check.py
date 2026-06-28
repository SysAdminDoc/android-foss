#!/usr/bin/env python3
"""Report duplicate and likely-fork identity signals in the catalog."""

from __future__ import annotations

from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
import re
import sys
from urllib.parse import urlparse

from catalog_check import AppEntry, README, parse_entries


GENERIC_REPO_SLUGS = {
    "android",
    "android-app",
    "android_app",
    "app",
    "client",
    "mobile",
    "mobile-app",
    "mobile_app",
    "tree",
}


@dataclass(frozen=True)
class IdentityFinding:
    classification: str
    key: str
    entries: tuple[AppEntry, ...]

    def format(self) -> str:
        locations = "; ".join(f"README.md:{entry.line_number} {entry.name} <{entry.source_url}>" for entry in self.entries)
        return f"{self.classification}: {self.key}: {locations}"


def load_entries() -> list[AppEntry]:
    entries, errors = parse_entries(README.read_text(encoding="utf-8").splitlines(keepends=True))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")
    return entries


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.casefold()).strip()


def normalize_source(url: str) -> str:
    return url.rstrip("/").casefold()


def repo_slug(url: str) -> str | None:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if not parts:
        return None
    slug = parts[-1].removesuffix(".git").casefold()
    slug = re.sub(r"[^a-z0-9._-]+", "-", slug).strip("-")
    if not slug or slug in GENERIC_REPO_SLUGS:
        return None
    return slug


def package_suffix(package_id: str) -> str | None:
    parts = [part for part in re.split(r"[._-]+", package_id.casefold()) if part]
    if len(parts) < 2:
        return None
    suffix = parts[-1]
    if suffix in {"app", "android", "client", "mobile", "fdroid", "free", "foss"}:
        return None
    return suffix


def duplicate_findings(entries: list[AppEntry]) -> list[IdentityFinding]:
    findings: list[IdentityFinding] = []
    grouped: dict[str, list[AppEntry]] = defaultdict(list)
    for entry in entries:
        grouped[normalize_name(entry.name)].append(entry)
    findings.extend(
        IdentityFinding("DUPLICATE_NAME", key, tuple(items))
        for key, items in sorted(grouped.items())
        if len(items) > 1
    )

    grouped.clear()
    for entry in entries:
        grouped[normalize_source(entry.source_url)].append(entry)
    findings.extend(
        IdentityFinding("DUPLICATE_SOURCE", key, tuple(items))
        for key, items in sorted(grouped.items())
        if len(items) > 1
    )
    return findings


def duplicate_package_findings(entries: list[AppEntry]) -> list[IdentityFinding]:
    grouped: dict[str, list[AppEntry]] = defaultdict(list)
    for entry in entries:
        for link in entry.store_links:
            if link.package_id:
                grouped[link.package_id.casefold()].append(entry)
    return [
        IdentityFinding("DUPLICATE_PACKAGE", key, tuple(items))
        for key, items in sorted(grouped.items())
        if len({item.line_number for item in items}) > 1
    ]


def likely_fork_findings(entries: list[AppEntry]) -> list[IdentityFinding]:
    findings: list[IdentityFinding] = []
    by_slug: dict[str, list[AppEntry]] = defaultdict(list)
    for entry in entries:
        slug = repo_slug(entry.source_url)
        if slug:
            by_slug[slug].append(entry)
    findings.extend(
        IdentityFinding("LIKELY_FORK_REPO_SLUG", key, tuple(items))
        for key, items in sorted(by_slug.items())
        if len({normalize_source(item.source_url) for item in items}) > 1
    )

    by_package_suffix: dict[str, list[AppEntry]] = defaultdict(list)
    for entry in entries:
        suffixes: set[str] = set()
        for link in entry.store_links:
            suffix = package_suffix(link.package_id)
            if suffix:
                suffixes.add(suffix)
        for suffix in suffixes:
            by_package_suffix[suffix].append(entry)
    findings.extend(
        IdentityFinding("LIKELY_FORK_PACKAGE_SUFFIX", key, tuple(items))
        for key, items in sorted(by_package_suffix.items())
        if len({item.line_number for item in items}) > 1
    )
    return findings


def main() -> int:
    parser = ArgumentParser(description="Report duplicate names, sources, package IDs, and likely fork variants.")
    parser.add_argument("--limit", type=int, default=None, help="print only the first N findings")
    args = parser.parse_args()

    entries = load_entries()
    findings = duplicate_findings(entries) + duplicate_package_findings(entries) + likely_fork_findings(entries)
    for finding in findings[: args.limit]:
        print(finding.format())

    counts: dict[str, int] = defaultdict(int)
    for finding in findings:
        counts[finding.classification] += 1
    summary = ", ".join(f"{key.lower()}={counts[key]}" for key in sorted(counts)) or "no findings"
    print(f"identity check completed: {len(entries)} entries, {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
