# Research - Android FOSS

## Executive Summary

Android FOSS is a GPL-3.0 curated Markdown catalog of 746 Android FOSS entries across 81 sections, with a lightweight browser renderer and local sorting/link scripts. Its strongest current shape is editorial selectivity: `CONTRIBUTING.md` requires FOSS licensing, privacy, stability, no proprietary elements, and active maintenance. The highest-value direction is to turn that editorial list into a trustable local-maintenance catalog: fix stale validators, add source-health checks, expose F-Droid/Izzy anti-feature and security metadata, harden `index.html`, and make discovery searchable without reintroducing hosted automation. Top opportunities: P0 validator repair; P0 renderer sanitization/CDN pinning; P0 archived/stale-source detection; P1 trust metadata overlays; P1 search/filter UI; P1 Android developer-verification guidance; P2 machine-readable catalog export; P2 accessibility/i18n pass; P2 contributor lint ergonomics.

## Product Map

- Core workflows: readers browse categories in `README.md`; contributors add alphabetized entries; maintainers run `python ensure_sorted.py`; `index.html` renders `README.md` in a browser; manual scripts check links and archived GitHub repos.
- User personas: privacy-first Android users replacing proprietary apps; FOSS contributors submitting projects; maintainers triaging inactive or moved projects; users affected by Android sideloading/developer-verification changes.
- Platforms and distribution: GitHub-hosted Markdown catalog plus local static `index.html`; Android app distribution links through F-Droid, IzzyOnDroid, project repos, and direct project sites.
- Key integrations and data flows: `README.md` contains source/store URLs; `ensure_sorted.py` parses category headers and app names; `check.sh` and `check_manually.sh` scrape links; `index.html` fetches local `README.md` and remote jsDelivr assets.

## Competitive Landscape

- F-Droid: does strong app metadata, anti-feature flags, reproducibility status, permissions, build logs, source links, and update channels. Learn from its trust fields and per-version transparency; avoid becoming a full app store or shipping APKs.
- IzzyOnDroid: emphasizes inclusion criteria, update recency, APK scanning, sensitive permission explanations, manifest checks, tracker/library screening, and removal rules. Learn from its risk annotations; avoid manual-only review with no repeatable local tooling.
- Awesome F-Droid Apps: provides a sortable/filterable table with stars, recency, repository source, and categories. Learn from searchable discovery and popularity/update signals; avoid ranking by stars alone.
- OpenAPK: surfaces latest, updated, featured, popular, hot, category, language, and developer submission views. Learn from discovery sections and multilingual presentation; avoid direct APK hosting responsibilities.
- Fossdroid: offers a searchable, trending, popular, and newest app UI over FOSS Android apps. Learn from simple discovery affordances; avoid opaque quality criteria.
- open-source-android-apps: uses generated category files, badges, hot-app sections, total app count, and contributor workflow. Learn from generated structure and metrics; avoid GitHub Actions because this fork intentionally removed hosted automation.
- Material You App List: tags entries with concise capability badges and gathers sources from communities. Learn from compact inline labels; avoid expanding beyond FOSS/privacy acceptance criteria.
- APKMirror and Google Play/AppBrain: closed/commercial ecosystems show what users expect from app catalogs: signature continuity, version history, variant/install compatibility warnings, SDK/library/privacy declarations, ads labels, and policy declarations. Learn from trust and compatibility explanations; avoid proprietary-store lock-in or paywalled ranking logic.

## Security, Privacy, and Reliability

- Verified: `index.html` injects `marked.parse(data)` into `innerHTML` without sanitization while Marked documents that output is not sanitized; contributor-controlled README content therefore needs DOMPurify or an equivalent sanitizer before HTML insertion.
- Verified: `index.html` loads Marked, marked-gfm-heading-id, and Bootswatch from jsDelivr at runtime with no SRI, lockfile, vendored fallback, or offline path; Bootswatch is currently pinned to 5.3.3 while jsDelivr shows 5.3.8.
- Verified: `check.sh` searches `https://f-droid.org/app` even though `CONTRIBUTING.md` and current entries use `https://f-droid.org/packages/<App ID>`; the script can pass while missing malformed current-format F-Droid package links.
- Verified: `check_manually.sh` scrapes GitHub HTML for the archived banner and treats all non-200 links as failures; this is brittle against redirects, rate limits, GitHub page text changes, GitLab/Codeberg archives, and transient CDN errors.
- Verified: recent history repeatedly removes inactive, archived, deprecated, moved, and dead-link projects; this is a root maintenance pain point, not a one-off.
- Verified: `README.md` contains 1,608 URLs and 746 app entries, but there is no repeatable source-health, license, anti-feature, sensitive-permission, or update-recency summary.
- Missing guardrails: no duplicate app/source/package detector, no source-host archive detector beyond manual GitHub HTML scraping, no known-vulnerability/anti-feature overlay, no signature/reproducibility metadata, no local static renderer security test.
- Recovery needs: local reports should be generated as non-committed artifacts so maintainers can review removals before editing `README.md`; link checks need retry/backoff and allowlists for expected non-200 endpoints.

## Architecture Assessment

- `README.md`: effective as the canonical human catalog, but too large for trust metadata and advanced discovery if every field remains hand-authored inline.
- `ensure_sorted.py`: useful narrow validator; should become or be joined by a structured parser that validates app line format, URL forms, duplicate names, duplicate repos, category order, store-link order, and current F-Droid/Izzy URL shapes.
- `check.sh`: refactor candidate; replace with a cross-platform Python check because WSL Bash is unavailable in this environment and the URL pattern is stale.
- `check_manually.sh`: refactor candidate; split link checking from source-health checks, use GitHub/GitLab/Codeberg APIs or lightweight HTTP endpoints, and classify archived/moved/not-found/rate-limited distinctly.
- `index.html`: refactor candidate; add sanitizer, pinned/vendored assets or integrity checks, accessible theme control, search/filter controls, local error UI, and a generated search index.
- Documentation gaps: no `ROADMAP.md` or `RESEARCH.md` existed before this pass; `CLAUDE.md` notes local checks but not link-health, renderer-security, or research cadence; contributor criteria do not specify stale-project, anti-feature, sensitive-permission, or developer-verification evidence.
- Test gaps: no automated tests for malformed app lines, F-Droid/Izzy URL extraction, duplicate entries, archived repo detection, index rendering, or XSS sanitization.

## Rejected Ideas

- Direct APK hosting: rejected because it changes the project from a catalog into a distribution repo and would require signing, malware scanning, takedown, version-retention, and compatibility infrastructure; source: APKMirror, OpenAPK, F-Droid.
- Hosted CI restoration: rejected because this fork intentionally removed GitHub Actions and Dependabot; implement local commands instead; source: `CHANGELOG.md`, `CLAUDE.md`, git history.
- Star-only ranking: rejected because Awesome F-Droid itself notes stars are imperfect; use stars only alongside recency, source health, F-Droid/Izzy availability, and trust metadata.
- Listing proprietary app-store links: rejected because `CONTRIBUTING.md` says not to submit third-party F-Droid repositories or Google Play Store links, and the catalog promise is FOSS/privacy-first.
- Replacing `README.md` with a database-only site: rejected because Markdown is the primary public artifact and contribution surface; add generated metadata around it instead.
- Broad non-Android/Linux-phone expansion: rejected because `doc/OpenAndroidProjects.md` already covers adjacent projects and the main catalog purpose is Android FOSS apps.

## Sources

### Project

- <https://github.com/SysAdminDoc/android-foss>
- <https://github.com/offa/android-foss>

### FOSS Catalogs and App Stores

- <https://f-droid.org/en/packages/org.fdroid.fdroid/>
- <https://f-droid.org/docs/Anti-Features/>
- <https://f-droid.org/docs/Reproducible_Builds/>
- <https://f-droid.org/en/docs/Build_Metadata_Reference/>
- <https://apt.izzysoft.de/fdroid/index/info>
- <https://android.izzysoft.de/articles/named/iod-scan-apkchecks>
- <https://github.com/moneytoo/awesome-fdroid>
- <https://github.com/pcqpcq/open-source-android-apps>
- <https://github.com/nyas1/Material-You-app-list>
- <https://fossdroid.com/>
- <https://www.openapk.net>

### Commercial and Adjacent Catalogs

- <https://www.apkmirror.com/faq/>
- <https://support.google.com/googleplay/android-developer/answer/9859455>
- <https://www.appbrain.com/stats/libraries>

### Platform and Policy

- <https://android-developers.googleblog.com/2025/08/elevating-android-security.html>
- <https://developer.android.com/google/play/integrity/remediation>
- <https://keepandroidopen.org/>
- <https://forum.f-droid.org/t/google-will-require-developer-verification-to-install-android-apps-including-sideloading/33123>
- <https://news.ycombinator.com/item?id=45507173>

### Community Signals

- <https://www.reddit.com/r/fossdroid/comments/1nnwupr/fdroids_search_feature_can_be_better/>
- <https://forum.f-droid.org/t/filter-out-apps-in-client-by-time-since-update/29919>
- <https://forum.f-droid.org/t/f-droid-app-should-warn-about-dangerous-permissions/15084>
- <https://www.reddit.com/r/PrivacyGuides/comments/u746sd/is_it_just_me_or_why_is_fdroid_such_a_mess_to/>
- <https://forum.f-droid.org/t/filter-options-for-search-on-f-droid-org-and-inside-the-f-droid-app/11355>

### Dependencies

- <https://marked.js.org/>
- <https://marked.js.org/using_advanced>
- <https://github.com/markedjs/marked-gfm-heading-id>
- <https://www.jsdelivr.com/package/npm/bootswatch>

## Open Questions

- Should the long-term catalog source remain hand-authored Markdown with generated sidecars, or should a structured data file become canonical while `README.md` is generated?
- Should entries with unresolved sensitive permissions or stale upstream releases be flagged in-place, moved to a generated report, or removed after a defined grace period?
