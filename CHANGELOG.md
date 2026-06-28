# Changelog

## Android FOSS v0.0.2 - 2026-06-28

- Added a cross-platform catalog checker for README entry markup, store URL formats, store-link order, and duplicate package IDs.
- Routed the legacy shell validation commands through the new local checker.
- Fixed malformed and stale F-Droid/IzzyOnDroid store links in the catalog.

## Android FOSS v0.0.1 - 2026-06-27

- Removed GitHub Actions and Dependabot configuration so checks and maintenance stay local.
- Added repository ignore rules for local working notes and editor files.
- Made the sorted-list validator read `README.md` as UTF-8 on Windows.
- Enforced LF line endings for shell scripts so local Bash checks run on Windows.
