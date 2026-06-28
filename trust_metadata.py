#!/usr/bin/env python3
"""Generate optional store trust metadata for the Android FOSS catalog."""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from catalog_check import AppEntry, README, parse_entries


FDROID_INDEX = "https://f-droid.org/repo/index-v1.json"
IZZY_INDEX = "https://apt.izzysoft.de/fdroid/repo/index-v1.json"
OUTPUT = Path("catalog-trust.json")
USER_AGENT = "android-foss-trust-metadata/0.1"

SENSITIVE_PERMISSIONS = {
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.CALL_PHONE",
    "android.permission.CAMERA",
    "android.permission.MANAGE_EXTERNAL_STORAGE",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.READ_CALENDAR",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_CONTACTS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_SMS",
    "android.permission.RECORD_AUDIO",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.WRITE_CALENDAR",
    "android.permission.WRITE_CONTACTS",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.WRITE_SETTINGS",
}


@dataclass(frozen=True)
class RepoIndex:
    name: str
    source: str
    timestamp: int | None
    apps: dict[str, dict[str, Any]]
    versions: dict[str, list[dict[str, Any]]]


def fetch_json(source: str, timeout: float) -> Any:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def index_versions(packages: Any) -> dict[str, list[dict[str, Any]]]:
    by_package: dict[str, list[dict[str, Any]]] = {}
    if isinstance(packages, list):
        for item in packages:
            if not isinstance(item, dict):
                continue
            package_name = item.get("packageName")
            if isinstance(package_name, str):
                by_package.setdefault(package_name, []).append(item)
    elif isinstance(packages, dict):
        for package_name, package_data in packages.items():
            if not isinstance(package_data, dict):
                continue
            versions = package_data.get("versions", {})
            if isinstance(versions, dict):
                by_package[package_name] = [version for version in versions.values() if isinstance(version, dict)]
    return by_package


def normalize_index(name: str, source: str, data: Any) -> RepoIndex:
    if not isinstance(data, dict):
        raise ValueError(f"{name} index did not return a JSON object")

    apps: dict[str, dict[str, Any]] = {}
    if isinstance(data.get("apps"), list):
        for app in data["apps"]:
            if isinstance(app, dict) and isinstance(app.get("packageName"), str):
                apps[app["packageName"]] = app
    elif isinstance(data.get("packages"), dict):
        for package_name, package_data in data["packages"].items():
            if isinstance(package_data, dict) and isinstance(package_data.get("metadata"), dict):
                metadata = dict(package_data["metadata"])
                metadata["packageName"] = package_name
                apps[package_name] = metadata

    repo = data.get("repo", {})
    timestamp = repo.get("timestamp") if isinstance(repo, dict) else None
    return RepoIndex(name, source, timestamp if isinstance(timestamp, int) else None, apps, index_versions(data.get("packages")))


def latest_version(versions: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not versions:
        return None
    return max(versions, key=lambda item: int(item.get("versionCode") or item.get("manifest", {}).get("versionCode") or 0))


def anti_features(app: dict[str, Any], version: dict[str, Any] | None) -> list[str]:
    values: set[str] = set()
    for source in (app.get("antiFeatures"), version.get("antiFeatures") if version else None):
        if isinstance(source, list):
            values.update(str(item) for item in source)
        elif isinstance(source, dict):
            values.update(str(item) for item in source)
    return sorted(values, key=str.casefold)


def manifest_permissions(version: dict[str, Any] | None) -> list[str]:
    if not version:
        return []
    manifest = version.get("manifest", {})
    permissions = manifest.get("usesPermission") if isinstance(manifest, dict) else None
    names: list[str] = []
    if isinstance(permissions, list):
        for permission in permissions:
            if isinstance(permission, dict) and isinstance(permission.get("name"), str):
                names.append(permission["name"])
    return sorted(set(names), key=str.casefold)


def millis_to_date(value: Any) -> str | None:
    if not isinstance(value, int):
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()


def verify_reproducible(package_id: str, timeout: float) -> bool | None:
    url = f"https://verification.f-droid.org/{package_id}.json"
    try:
        data = fetch_json(url, timeout)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise
    except (TimeoutError, URLError):
        return None
    if isinstance(data, dict) and isinstance(data.get("lastRunVerified"), bool):
        return data["lastRunVerified"]
    return None


def package_metadata(
    store: str,
    package_id: str,
    repo: RepoIndex,
    verify: bool,
    timeout: float,
) -> dict[str, Any] | None:
    app = repo.apps.get(package_id)
    if app is None:
        return None
    version = latest_version(repo.versions.get(package_id, []))
    permissions = manifest_permissions(version)
    sensitive = [permission for permission in permissions if permission in SENSITIVE_PERMISSIONS]
    source_available = bool(version and isinstance(version.get("src"), dict))

    item: dict[str, Any] = {
        "store": store,
        "packageId": package_id,
        "repository": repo.name,
        "license": app.get("license"),
        "sourceCode": app.get("sourceCode"),
        "lastUpdated": millis_to_date(app.get("lastUpdated")),
        "antiFeatures": anti_features(app, version),
        "permissionCount": len(permissions),
        "sensitivePermissions": sensitive,
        "sourceArchive": source_available,
        "reproducible": None,
    }
    if store == "F-Droid" and verify:
        item["reproducible"] = verify_reproducible(package_id, timeout)
    return item


def build_catalog(
    entries: list[AppEntry],
    fdroid: RepoIndex,
    izzy: RepoIndex,
    verify: bool,
    timeout: float,
    limit: int | None = None,
) -> dict[str, Any]:
    selected = entries[:limit] if limit else entries
    output_entries: dict[str, Any] = {}
    coverage = {"entries": 0, "packages": 0}

    for entry in selected:
        packages: list[dict[str, Any]] = []
        for link in entry.store_links:
            repo = fdroid if link.store == "F-Droid" else izzy
            metadata = package_metadata(link.store, link.package_id, repo, verify, timeout)
            if metadata is not None:
                packages.append(metadata)
        if packages:
            output_entries[entry.name] = {
                "line": entry.line_number,
                "sourceUrl": entry.source_url,
                "packages": packages,
            }
            coverage["entries"] += 1
            coverage["packages"] += len(packages)

    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "sources": {
            "fdroid": {"url": fdroid.source, "timestamp": fdroid.timestamp},
            "izzy": {"url": izzy.source, "timestamp": izzy.timestamp},
        },
        "coverage": coverage,
        "entries": output_entries,
    }


def load_entries() -> list[AppEntry]:
    entries, errors = parse_entries(README.read_text(encoding="utf-8").splitlines(keepends=True))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit("catalog has structural errors; run python catalog_check.py first")
    return entries


def main() -> int:
    parser = ArgumentParser(description="Generate catalog-trust.json from F-Droid and IzzyOnDroid indexes.")
    parser.add_argument("--fdroid-index", default=FDROID_INDEX, help="F-Droid index URL or local JSON path")
    parser.add_argument("--izzy-index", default=IZZY_INDEX, help="IzzyOnDroid index URL or local JSON path")
    parser.add_argument("--output", default=str(OUTPUT), help="metadata JSON output path")
    parser.add_argument("--limit", type=int, default=None, help="only process the first N README entries")
    parser.add_argument("--timeout", type=float, default=45.0, help="network timeout in seconds")
    parser.add_argument("--verify-reproducible", action="store_true", help="query verification.f-droid.org for F-Droid packages")
    args = parser.parse_args()

    fdroid = normalize_index("F-Droid", args.fdroid_index, fetch_json(args.fdroid_index, args.timeout))
    izzy = normalize_index("IzzyOnDroid", args.izzy_index, fetch_json(args.izzy_index, args.timeout))
    catalog = build_catalog(load_entries(), fdroid, izzy, args.verify_reproducible, args.timeout, args.limit)

    output = Path(args.output)
    output.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coverage = catalog["coverage"]
    print(f"wrote {output}: {coverage['entries']} entries, {coverage['packages']} package metadata records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
