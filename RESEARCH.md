# Research: Android FOSS

Updated for Android FOSS v0.0.14 on September 6, 2026.

## Product position

Android FOSS is a GPLv3 catalog for people who want open-source Android apps without wading through store rankings or opaque recommendation lists. The current catalog contains 767 apps across 84 categories, with 831 links to F-Droid and IzzyOnDroid packages.

The README remains the contribution surface and long-form catalog. The browser turns generated catalog data into a faster discovery experience with search, sorting, source links, store filters, update dates, popularity signals, and published trust metadata.

The product promise is deliberately narrow. It helps people compare evidence before installing an app. It doesn't certify that an app is safe or suitable for a particular device.

## Audience

- Android users looking for free and open-source replacements
- Privacy-conscious users who want source and store evidence close at hand
- Contributors adding or correcting catalog entries
- Maintainers checking stale sources, store metadata, and acceptance criteria

## Competitive references

F-Droid and IzzyOnDroid set the strongest examples for package transparency. Their anti-feature labels, reproducibility notes, permissions, source archives, and update records informed the trust fields used here.

Awesome F-Droid Apps, Fossdroid, OpenAPK, and Material You App List show the value of quick search and compact discovery signals. Android FOSS borrows those useful patterns while keeping its own privacy-focused acceptance criteria and source-first presentation.

Commercial stores also shape user expectations around version history, signing continuity, compatibility, and privacy declarations. Those ideas are useful reference points, but Android FOSS doesn't host APKs or rank apps through paid placement.

## Current architecture

- `README.md` is the human-edited source catalog.
- `catalog.json` supplies app names, categories, sources, stores, packages, and README locations.
- `catalog-trust.json` records available F-Droid and IzzyOnDroid evidence.
- `catalog-popularity.json` adds GitHub discovery signals when they are available.
- `index.html` and local assets provide the installable catalog experience without third-party runtime dependencies.
- Local checks cover catalog structure, ordering, changed-entry acceptance, source health, generated metadata, and frontend behavior.

The browser defaults to the strongest available signal coverage instead of star count. Stars can help discovery, but they don't prove privacy, maintenance quality, or security.

## Reliability and privacy decisions

- All browser code, styles, fonts, icons, and data ship with the project. The catalog doesn't need a remote JavaScript or CSS service to open.
- Search and filters run in the browser. Queries aren't sent to an analytics service.
- Trust labels describe published metadata. The interface repeats that these labels aren't a safety guarantee.
- Source checks classify moved, archived, missing, rate-limited, and active links so maintainers can review changes before removal.
- Release ZIPs are deterministic and include a SHA256 checksum.

## Maintenance priorities

- Recheck moved or deleted projects before each catalog release.
- Regenerate trust data after any store-link change.
- Keep screenshots and visible totals in sync with generated catalog data.
- Expand non-GitHub update signals when a dependable source is available.

## Rejected directions

Direct APK hosting would turn the project into a software distributor with signing, malware-scanning, retention, and takedown duties. That isn't the catalog's job.

Star-only ranking was also rejected. A large audience doesn't replace source review, current releases, or store metadata.

The project won't add proprietary app-store links. The contribution criteria remain focused on free and open-source software.

## Sources

### Project

- <https://github.com/SysAdminDoc/android-foss>
- <https://github.com/offa/android-foss>

### FOSS catalogs and app stores

- <https://f-droid.org/en/packages/org.fdroid.fdroid/>
- <https://f-droid.org/docs/Anti-Features/>
- <https://f-droid.org/docs/Reproducible_Builds/>
- <https://apt.izzysoft.de/fdroid/index/info>
- <https://android.izzysoft.de/articles/named/iod-scan-apkchecks>
- <https://github.com/moneytoo/awesome-fdroid>
- <https://github.com/nyas1/Material-You-app-list>
- <https://fossdroid.com/>
- <https://www.openapk.net>

### Android platform

- <https://developer.android.com/google/play/integrity/remediation>
- <https://keepandroidopen.org/>

## Open questions

- Should the README stay canonical if structured contributions become easier to review?
- What grace period should apply when an upstream source disappears or stops publishing releases?
