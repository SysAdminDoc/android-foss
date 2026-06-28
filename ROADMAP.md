# Roadmap

## Research-Driven Additions

- [ ] P0 - Replace stale link validators with one cross-platform local checker
  Why: `check.sh` still searches the old `f-droid.org/app` pattern while current entries use `f-droid.org/packages`, and Bash checks are not reliable on this Windows maintenance environment.
  Evidence: `check.sh`; `CONTRIBUTING.md`; F-Droid metadata docs.
  Touches: `check.sh`, `check_manually.sh`, `ensure_sorted.py`, new local checker module/script.
  Acceptance: A single local command validates F-Droid and Izzy URL formats, duplicate entries, store-link order, malformed Markdown lines, and exits non-zero with actionable line numbers.
  Complexity: M

- [ ] P0 - Harden `index.html` Markdown rendering
  Why: Marked explicitly does not sanitize output, but `index.html` injects parsed README HTML directly into `innerHTML` and loads remote runtime assets without integrity or offline fallback.
  Evidence: `index.html`; Marked security documentation; jsDelivr Bootswatch package page.
  Touches: `index.html`, optional vendored static assets, local render smoke test.
  Acceptance: Rendered README HTML is sanitized, remote assets are pinned with integrity or vendored locally, load failures show an in-page error, and an XSS fixture cannot execute script.
  Complexity: M

- [ ] P0 - Add archived, moved, stale, and missing-source health checks
  Why: Recent commits repeatedly remove inactive, archived, deprecated, moved, and dead projects, but the repo has only brittle manual GitHub HTML scraping.
  Evidence: `rtk git log -200`; `check_manually.sh`; IzzyOnDroid inclusion/removal policy.
  Touches: new local health checker, `check_manually.sh`, README entry parser.
  Acceptance: Local report classifies GitHub/GitLab/Codeberg/source URLs as active, archived, moved, missing, rate-limited, or stale, with line numbers and no automatic README edits.
  Complexity: L

- [ ] P1 - Surface trust metadata for F-Droid and Izzy-backed entries
  Why: F-Droid and Izzy expose anti-features, reproducibility/build metadata, permissions, sensitive-permission explanations, and security scanning signals that the list does not currently show.
  Evidence: F-Droid Anti-Features; F-Droid Reproducible Builds; F-Droid Build Metadata Reference; IzzyOnDroid security info.
  Touches: README parser, generated metadata cache, `index.html`, contributor criteria.
  Acceptance: Entries with available metadata can display source/store, anti-feature, reproducibility, sensitive-permission, and last-update indicators without hand-copying every field into README lines.
  Complexity: L

- [ ] P1 - Add local search and filters to the static browser view
  Why: Competing catalogs and community feedback consistently value search, category filtering, update recency, popularity, and compatibility filters over a long alphabetic page.
  Evidence: Awesome F-Droid Apps; Fossdroid; OpenAPK; F-Droid forum and Reddit search/filter complaints.
  Touches: `index.html`, generated search index, README parser.
  Acceptance: Browser view supports text search plus category, F-Droid/Izzy availability, source host, trust flag, and update-recency filters while preserving the README as source content.
  Complexity: L

- [ ] P1 - Document Android developer-verification and sideloading impact
  Why: Android developer verification begins regionally in September 2026 and expands globally from 2027, directly affecting users who install apps outside Google Play.
  Evidence: Android Developers Blog; Keep Android Open; F-Droid forum; Hacker News discussion.
  Touches: `README.md`, `doc/OpenAndroidProjects.md`, contributor criteria.
  Acceptance: The catalog explains verified-developer requirements, affected regions/timeline, F-Droid/Izzy implications, and safe install/update guidance without endorsing proprietary lock-in.
  Complexity: S

- [ ] P1 - Add contributor-facing acceptance lint for privacy and maintenance criteria
  Why: `CONTRIBUTING.md` states privacy, no proprietary elements, stability, and active maintenance requirements, but local checks do not verify evidence for those criteria.
  Evidence: `CONTRIBUTING.md`; F-Droid Anti-Features; IzzyOnDroid inclusion policy.
  Touches: `CONTRIBUTING.md`, local checker, README parser.
  Acceptance: New or changed entries are checked for source URL, license evidence, app-store link order, active upstream signal, and known anti-feature flags before maintainers review content.
  Complexity: M

- [ ] P2 - Generate a machine-readable catalog sidecar
  Why: Trust overlays, search, duplicate detection, and future exports are fragile if every field must be reparsed from Markdown each time.
  Evidence: 746 README entries; Awesome F-Droid generated table; open-source-android-apps generated categories.
  Touches: README parser, generated JSON sidecar, local checker, `index.html`.
  Acceptance: A local command emits deterministic JSON containing app name, category, source URL, store links, package IDs, source host, and line number, and README remains the visible canonical catalog.
  Complexity: M

- [ ] P2 - Add duplicate, fork, and package-identity detection
  Why: Android users need to know whether similarly named entries are forks, package variants, or duplicate listings; community complaints cite uncertainty about legitimate apps.
  Evidence: PrivacyGuides Reddit thread; F-Droid package identity model; APKMirror signature/variant FAQ.
  Touches: README parser, local checker, generated metadata cache.
  Acceptance: Local checks report duplicate names, duplicate source URLs, duplicate package IDs, and likely fork variants with review-friendly classifications.
  Complexity: M

- [ ] P2 - Improve accessibility and responsive behavior of `index.html`
  Why: The renderer has a fixed bottom-right unlabeled theme selector and minimal layout semantics, while the README is a long navigation-heavy document.
  Evidence: `index.html`; F-Droid forum search/filter complaints; browser accessibility expectations.
  Touches: `index.html`, CSS, render smoke test.
  Acceptance: The browser view has labeled controls, keyboard-reachable navigation, visible focus states, no clipped content on mobile widths, and theme state that does not obscure content.
  Complexity: M

- [ ] P2 - Add optional localization hooks for the browser view
  Why: OpenAPK and F-Droid expose multilingual surfaces, and Android FOSS users are global, but the current browser chrome is English-only.
  Evidence: OpenAPK language switcher; F-Droid localized docs and app pages.
  Touches: `index.html`, small locale dictionary, generated search labels.
  Acceptance: UI labels in the static renderer can be translated without duplicating README content or changing the Markdown catalog format.
  Complexity: S

- [ ] P3 - Add popularity and recency signals as advisory filters
  Why: Stars, latest releases, updated apps, and trending lists help discovery, but star-only ranking is weak and should be advisory.
  Evidence: Awesome F-Droid Apps; OpenAPK; Fossdroid; AppBrain statistics model.
  Touches: metadata fetcher, generated cache, `index.html`.
  Acceptance: Optional generated metadata shows source-host stars and last release/update timestamps where available, clearly labeled as discovery aids rather than quality guarantees.
  Complexity: L
