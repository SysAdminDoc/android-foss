# Roadmap

## Research-Driven Additions

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
