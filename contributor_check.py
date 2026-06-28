#!/usr/bin/env python3
"""Contributor-facing acceptance checks for changed README catalog entries."""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from catalog_check import AppEntry, README, parse_entries, validate_duplicate_packages
from source_health import SourceTarget, classify


TRUST_METADATA = Path("catalog-trust.json")
BLOCKED_ANTI_FEATURES = {"KnownVuln", "NonFreeComp", "Tracking"}


@dataclass(frozen=True)
class Finding:
    level: str
    line: int
    name: str
    message: str

    def format(self) -> str:
        return f"{self.level}: README.md:{self.line}: {self.name}: {self.message}"


def diff_added_lines(args: list[str]) -> set[int]:
    result = subprocess.run(
        ["git", *args, "--unified=0", "--", str(README)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.strip() or "git diff failed")

    lines: set[int] = set()
    for match in re.finditer(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@", result.stdout, re.MULTILINE):
        start = int(match.group("start"))
        count = int(match.group("count") or "1")
        lines.update(range(start, start + count))
    return lines


def changed_readme_lines() -> set[int]:
    return diff_added_lines(["diff"]) | diff_added_lines(["diff", "--cached"])


def load_entries() -> list[AppEntry]:
    entries, errors = parse_entries(README.read_text(encoding="utf-8").splitlines(keepends=True))
    validate_duplicate_packages(entries, errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")
    return entries


def load_trust_metadata() -> dict[str, dict[str, object]]:
    if not TRUST_METADATA.exists():
        return {}
    data = json.loads(TRUST_METADATA.read_text(encoding="utf-8"))
    entries = data.get("entries", {})
    return entries if isinstance(entries, dict) else {}


def trust_packages(entry: AppEntry, trust: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    metadata = trust.get(entry.name)
    packages = metadata.get("packages") if isinstance(metadata, dict) else None
    if not isinstance(packages, list):
        return []
    return [package for package in packages if isinstance(package, dict)]


def check_metadata(entry: AppEntry, trust: dict[str, dict[str, object]]) -> list[Finding]:
    findings: list[Finding] = []
    packages = trust_packages(entry, trust)
    if entry.store_links and not packages:
        findings.append(Finding("WARN", entry.line_number, entry.name, "store metadata missing; run python trust_metadata.py"))
        return findings

    for package in packages:
        package_id = package.get("packageId") or "unknown package"
        license_name = package.get("license")
        if not isinstance(license_name, str) or not license_name:
            findings.append(Finding("WARN", entry.line_number, entry.name, f"{package_id} has no license metadata"))
        if not package.get("lastUpdated"):
            findings.append(Finding("WARN", entry.line_number, entry.name, f"{package_id} has no last-update metadata"))

        anti_features = package.get("antiFeatures")
        if isinstance(anti_features, list):
            blocked = sorted(str(item) for item in anti_features if str(item) in BLOCKED_ANTI_FEATURES)
            if blocked:
                findings.append(
                    Finding("ERROR", entry.line_number, entry.name, f"{package_id} has blocked anti-features: {', '.join(blocked)}")
                )
            elif anti_features:
                findings.append(
                    Finding("WARN", entry.line_number, entry.name, f"{package_id} has anti-features: {', '.join(map(str, anti_features))}")
                )
    return findings


def check_source_url(entry: AppEntry) -> list[Finding]:
    parsed = urlparse(entry.source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return [Finding("ERROR", entry.line_number, entry.name, "source URL must be an absolute HTTP(S) URL")]
    if parsed.scheme != "https":
        return [Finding("WARN", entry.line_number, entry.name, "source URL is not HTTPS")]
    return []


def check_source_health(entry: AppEntry, timeout: float, stale_days: int) -> list[Finding]:
    result = classify(SourceTarget(entry.source_url, (entry.name,), (entry.line_number,)), timeout, stale_days)
    if result.status in {"archived", "missing", "moved"}:
        return [Finding("ERROR", entry.line_number, entry.name, f"source is {result.status}: {result.detail}")]
    if result.status in {"rate-limited", "stale"}:
        return [Finding("WARN", entry.line_number, entry.name, f"source is {result.status}: {result.detail}")]
    return []


def check_entries(entries: list[AppEntry], trust: dict[str, dict[str, object]], skip_network: bool, timeout: float, stale_days: int) -> list[Finding]:
    findings: list[Finding] = []
    for entry in entries:
        findings.extend(check_source_url(entry))
        findings.extend(check_metadata(entry, trust))
        if not skip_network:
            findings.extend(check_source_health(entry, timeout, stale_days))
    return findings


def main() -> int:
    parser = ArgumentParser(description="Check changed README entries against contributor acceptance criteria.")
    parser.add_argument("--all", action="store_true", help="check every README catalog entry instead of changed entries")
    parser.add_argument("--skip-network", action="store_true", help="skip live source-health checks")
    parser.add_argument("--timeout", type=float, default=10.0, help="source-health request timeout in seconds")
    parser.add_argument("--stale-days", type=int, default=730, help="source pushed_at age that counts as stale")
    args = parser.parse_args()

    entries = load_entries()
    if args.all:
        selected = entries
    else:
        changed = changed_readme_lines()
        selected = [entry for entry in entries if entry.line_number in changed]

    if not selected:
        print("contributor check skipped: no changed README catalog entries")
        return 0

    findings = check_entries(selected, load_trust_metadata(), args.skip_network, args.timeout, args.stale_days)
    for finding in findings:
        print(finding.format(), file=sys.stderr if finding.level == "ERROR" else sys.stdout)

    errors = sum(1 for finding in findings if finding.level == "ERROR")
    warnings = sum(1 for finding in findings if finding.level == "WARN")
    print(f"contributor check completed: {len(selected)} entries, {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
