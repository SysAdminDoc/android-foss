#!/usr/bin/env python3
"""Generate optional advisory popularity and source recency metadata."""

from __future__ import annotations

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from catalog_check import README, parse_entries


OUTPUT = Path("catalog-popularity.json")
USER_AGENT = "android-foss-popularity-metadata/0.1"


@dataclass(frozen=True)
class GitHubRepo:
    source_url: str
    api_name: str


def github_token() -> str | None:
    result = subprocess.run(["gh", "auth", "token"], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    token = result.stdout.strip()
    return token or None


def github_repo(source_url: str) -> GitHubRepo | None:
    parsed = urlparse(source_url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1].removesuffix(".git")
    return GitHubRepo(source_url, f"{owner}/{repo}")


def request_json(url: str, token: str | None, timeout: float) -> tuple[int, Any]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        return response.status, json.load(response)


def date_only(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def fetch_repo_metadata(repo: GitHubRepo, token: str | None, timeout: float) -> dict[str, Any]:
    data: dict[str, Any] = {
        "sourceUrl": repo.source_url,
        "sourceHost": "github.com",
        "repository": repo.api_name,
        "stars": None,
        "forks": None,
        "openIssues": None,
        "sourceUpdated": None,
        "sourcePushed": None,
        "latestReleaseTag": None,
        "latestReleaseDate": None,
        "available": False,
    }
    try:
        _, repo_data = request_json(f"https://api.github.com/repos/{repo.api_name}", token, timeout)
        data.update(
            {
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "openIssues": repo_data.get("open_issues_count"),
                "sourceUpdated": date_only(repo_data.get("updated_at")),
                "sourcePushed": date_only(repo_data.get("pushed_at")),
                "available": True,
            }
        )
    except (HTTPError, TimeoutError, URLError):
        return data

    try:
        _, release_data = request_json(f"https://api.github.com/repos/{repo.api_name}/releases/latest", token, timeout)
        data["latestReleaseTag"] = release_data.get("tag_name")
        data["latestReleaseDate"] = date_only(release_data.get("published_at"))
    except HTTPError as error:
        if error.code != 404:
            data["latestReleaseTag"] = None
    except (TimeoutError, URLError):
        pass
    return data


def load_github_repos(limit: int | None) -> dict[str, GitHubRepo]:
    entries, errors = parse_entries(README.read_text(encoding="utf-8").splitlines(keepends=True))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")

    repos: dict[str, GitHubRepo] = {}
    for entry in entries:
        repo = github_repo(entry.source_url)
        if repo:
            repos.setdefault(repo.api_name.casefold(), repo)
        if limit and len(repos) >= limit:
            break
    return repos


def build_metadata(limit: int | None, workers: int, timeout: float) -> dict[str, Any]:
    token = github_token()
    repos = load_github_repos(limit)
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(fetch_repo_metadata, repo, token, timeout) for repo in repos.values()]
        for future in as_completed(futures):
            metadata = future.result()
            results[metadata["sourceUrl"]] = metadata
    return {
        "schemaVersion": 1,
        "source": "GitHub REST API",
        "advisory": "Stars and release dates are discovery aids, not quality or safety guarantees.",
        "coverage": {
            "repositories": len(results),
            "available": sum(1 for item in results.values() if item.get("available") is True),
        },
        "sources": dict(sorted(results.items())),
    }


def main() -> int:
    parser = ArgumentParser(description="Generate optional GitHub popularity and source-recency metadata.")
    parser.add_argument("--output", default=str(OUTPUT), help="JSON output path")
    parser.add_argument("--limit", type=int, default=None, help="only fetch the first N unique GitHub repositories")
    parser.add_argument("--workers", type=int, default=8, help="parallel GitHub request workers")
    parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")
    args = parser.parse_args()

    metadata = build_metadata(args.limit, args.workers, args.timeout)
    output = Path(args.output)
    output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coverage = metadata["coverage"]
    print(f"wrote {output}: {coverage['available']} available of {coverage['repositories']} GitHub repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
