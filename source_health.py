#!/usr/bin/env python3
"""Report source URL health for the Android FOSS catalog."""

from __future__ import annotations

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from catalog_check import README, parse_entries


USER_AGENT = "android-foss-source-health/0.1"


@dataclass(frozen=True)
class SourceTarget:
    url: str
    names: tuple[str, ...]
    lines: tuple[int, ...]


@dataclass(frozen=True)
class HealthResult:
    url: str
    status: str
    detail: str
    names: tuple[str, ...]
    lines: tuple[int, ...]
    final_url: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "detail": self.detail,
            "names": self.names,
            "lines": self.lines,
            "final_url": self.final_url,
        }


def load_targets(limit: int | None, host: str | None) -> list[SourceTarget]:
    entries, errors = parse_entries(README.read_text(encoding="utf-8").splitlines(keepends=True))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")

    grouped: dict[str, tuple[list[str], list[int]]] = {}
    for entry in entries:
        parsed = urlparse(entry.source_url)
        if parsed.scheme not in {"http", "https"}:
            continue
        names, lines = grouped.setdefault(entry.source_url, ([], []))
        names.append(entry.name)
        lines.append(entry.line_number)

    targets = [
        SourceTarget(url=url, names=tuple(names), lines=tuple(lines))
        for url, (names, lines) in sorted(grouped.items(), key=lambda item: item[0].casefold())
    ]
    if host:
        targets = [target for target in targets if urlparse(target.url).netloc.lower() == host.lower()]
    return targets[:limit] if limit else targets


def request_json(url: str, timeout: float) -> tuple[int, str, dict[str, str], Any]:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.status, response.geturl(), dict(response.headers), json.load(response)


def request_url(url: str, timeout: float, method: str) -> tuple[int, str, dict[str, str]]:
    request = Request(url, method=method, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.status, response.geturl(), dict(response.headers)


def github_api_url(source_url: str) -> str | None:
    parsed = urlparse(source_url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1].removesuffix(".git")
    return f"https://api.github.com/repos/{owner}/{repo}"


def classify_github(target: SourceTarget, timeout: float, stale_days: int) -> HealthResult | None:
    api_url = github_api_url(target.url)
    if api_url is None:
        return None

    try:
        _, final_url, headers, data = request_json(api_url, timeout)
    except HTTPError as error:
        if error.code == 403 and error.headers.get("X-RateLimit-Remaining") == "0":
            return HealthResult(target.url, "rate-limited", "GitHub API rate limit reached", target.names, target.lines)
        if error.code == 404:
            return HealthResult(target.url, "missing", "GitHub repository returned 404", target.names, target.lines)
        return HealthResult(target.url, "missing", f"GitHub API HTTP {error.code}", target.names, target.lines)
    except (TimeoutError, URLError) as error:
        return HealthResult(target.url, "missing", f"GitHub API request failed: {error}", target.names, target.lines)

    if final_url.rstrip("/") != api_url.rstrip("/"):
        return HealthResult(target.url, "moved", f"GitHub API redirected to {final_url}", target.names, target.lines, final_url)

    html_url = str(data.get("html_url", "")).rstrip("/")
    if html_url and html_url.casefold() != target.url.rstrip("/").casefold():
        return HealthResult(target.url, "moved", f"GitHub canonical URL is {html_url}", target.names, target.lines, html_url)

    if data.get("archived") is True:
        return HealthResult(target.url, "archived", "GitHub repository is archived", target.names, target.lines, html_url)

    pushed_at = data.get("pushed_at")
    if isinstance(pushed_at, str):
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - pushed).days
        if age_days >= stale_days:
            return HealthResult(target.url, "stale", f"last pushed {age_days} days ago", target.names, target.lines, html_url)
        return HealthResult(target.url, "active", f"last pushed {age_days} days ago", target.names, target.lines, html_url)

    remaining = headers.get("X-RateLimit-Remaining")
    detail = f"GitHub repository reachable; rate remaining {remaining}" if remaining else "GitHub repository reachable"
    return HealthResult(target.url, "active", detail, target.names, target.lines, html_url)


def classify_http(target: SourceTarget, timeout: float) -> HealthResult:
    try:
        status, final_url, _ = request_url(target.url, timeout, "HEAD")
    except HTTPError as error:
        if error.code in {405, 501}:
            return classify_http_get(target, timeout)
        if error.code == 404:
            return HealthResult(target.url, "missing", "HTTP 404", target.names, target.lines)
        if error.code == 429:
            return HealthResult(target.url, "rate-limited", "HTTP 429", target.names, target.lines)
        if error.code in {301, 302, 303, 307, 308}:
            location = error.headers.get("Location")
            return HealthResult(target.url, "moved", f"HTTP {error.code} to {location}", target.names, target.lines, location)
        return HealthResult(target.url, "missing", f"HTTP {error.code}", target.names, target.lines)
    except (TimeoutError, URLError) as error:
        return HealthResult(target.url, "missing", f"request failed: {error}", target.names, target.lines)

    if status == 429:
        return HealthResult(target.url, "rate-limited", "HTTP 429", target.names, target.lines, final_url)
    if status >= 400:
        return HealthResult(target.url, "missing", f"HTTP {status}", target.names, target.lines, final_url)
    if final_url.rstrip("/") != target.url.rstrip("/"):
        return HealthResult(target.url, "moved", f"redirected to {final_url}", target.names, target.lines, final_url)
    return HealthResult(target.url, "active", f"HTTP {status}", target.names, target.lines, final_url)


def classify_http_get(target: SourceTarget, timeout: float) -> HealthResult:
    try:
        status, final_url, _ = request_url(target.url, timeout, "GET")
    except HTTPError as error:
        if error.code == 404:
            return HealthResult(target.url, "missing", "HTTP 404", target.names, target.lines)
        if error.code == 429:
            return HealthResult(target.url, "rate-limited", "HTTP 429", target.names, target.lines)
        return HealthResult(target.url, "missing", f"HTTP {error.code}", target.names, target.lines)
    except (TimeoutError, URLError) as error:
        return HealthResult(target.url, "missing", f"request failed: {error}", target.names, target.lines)

    if final_url.rstrip("/") != target.url.rstrip("/"):
        return HealthResult(target.url, "moved", f"redirected to {final_url}", target.names, target.lines, final_url)
    return HealthResult(target.url, "active", f"HTTP {status}", target.names, target.lines, final_url)


def classify(target: SourceTarget, timeout: float, stale_days: int) -> HealthResult:
    github = classify_github(target, timeout, stale_days)
    if github is not None:
        return github
    return classify_http(target, timeout)


def print_text(results: list[HealthResult]) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    summary = ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
    print(f"source health checked {len(results)} URL(s): {summary}")
    for result in results:
        lines = ",".join(str(line) for line in result.lines)
        names = "; ".join(result.names[:3])
        if len(result.names) > 3:
            names += "; ..."
        print(f"{result.status.upper():12} README.md:{lines} {result.url} | {names} | {result.detail}")


def main() -> int:
    parser = ArgumentParser(description="Classify source URL health without editing README.md.")
    parser.add_argument("--limit", type=int, default=None, help="check only the first N unique source URLs")
    parser.add_argument("--timeout", type=float, default=12.0, help="per-request timeout in seconds")
    parser.add_argument("--workers", type=int, default=8, help="parallel request workers")
    parser.add_argument("--stale-days", type=int, default=730, help="GitHub pushed_at age that counts as stale")
    parser.add_argument("--host", default=None, help="check only source URLs from this host")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    targets = load_targets(args.limit, args.host)
    results: list[HealthResult] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(classify, target, args.timeout, args.stale_days) for target in targets]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda result: (result.status, result.url.casefold()))
    if args.json:
        print(json.dumps([result.as_dict() for result in results], indent=2))
    else:
        print_text(results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
