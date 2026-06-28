# Changelog

## Android FOSS v0.0.9 - 2026-06-28

- Added a deterministic machine-readable catalog sidecar generated from `README.md`.
- Exported entry names, categories, source URLs, source hosts, store links, package IDs, and README line numbers.

## Android FOSS v0.0.8 - 2026-06-28

- Added a contributor-facing acceptance checker for changed README catalog entries.
- Checked source URL shape, trust metadata evidence, blocked anti-features, and live source-health signals before review.

## Android FOSS v0.0.7 - 2026-06-28

- Documented Android developer-verification timing, affected install paths, and F-Droid/IzzyOnDroid implications.
- Added contributor guidance for signing, release-channel, and developer-verification evidence.

## Android FOSS v0.0.6 - 2026-06-28

- Added local browser search over app names, categories, package IDs, source hosts, and store names.
- Added category, store, source-host, trust-flag, and update-recency filters to the static catalog view.

## Android FOSS v0.0.5 - 2026-06-28

- Added a generated F-Droid and IzzyOnDroid trust metadata sidecar for catalog entries.
- Displayed store, anti-feature, sensitive-permission, update, source-archive, and reproducible-build indicators in the static browser view when metadata is available.
- Added offline unit coverage for trust metadata extraction.

## Android FOSS v0.0.4 - 2026-06-28

- Added a local source-health reporter for archived, moved, stale, missing, active, and rate-limited source URLs.
- Routed the manual shell check through the source-health report with README line-numbered output.
- Added offline unit coverage for source-health classifier states.

## Android FOSS v0.0.3 - 2026-06-28

- Hardened the static browser renderer with local vendored assets and sanitized Markdown output.
- Added in-page catalog load errors and a labeled theme selector that works across desktop and mobile widths.

## Android FOSS v0.0.2 - 2026-06-28

- Added a cross-platform catalog checker for README entry markup, store URL formats, store-link order, and duplicate package IDs.
- Routed the legacy shell validation commands through the new local checker.
- Fixed malformed and stale F-Droid/IzzyOnDroid store links in the catalog.

## Android FOSS v0.0.1 - 2026-06-27

- Removed GitHub Actions and Dependabot configuration so checks and maintenance stay local.
- Added repository ignore rules for local working notes and editor files.
- Made the sorted-list validator read `README.md` as UTF-8 on Windows.
- Enforced LF line endings for shell scripts so local Bash checks run on Windows.
