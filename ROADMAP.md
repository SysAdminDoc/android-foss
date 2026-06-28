# Roadmap

## Research-Driven Additions

- [ ] P3 - Add popularity and recency signals as advisory filters
  Why: Stars, latest releases, updated apps, and trending lists help discovery, but star-only ranking is weak and should be advisory.
  Evidence: Awesome F-Droid Apps; OpenAPK; Fossdroid; AppBrain statistics model.
  Touches: metadata fetcher, generated cache, `index.html`.
  Acceptance: Optional generated metadata shows source-host stars and last release/update timestamps where available, clearly labeled as discovery aids rather than quality guarantees.
  Complexity: L
