# Roadmap

## Research-Driven Additions

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
