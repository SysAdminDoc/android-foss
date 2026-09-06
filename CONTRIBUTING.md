# Criteria

Every listed app must meet these criteria:

1. Licensed as free and open-source software
1. Public source code
1. Protects privacy. No advertising or spyware.
1. No proprietary elements
1. Stable enough for regular use
1. Actively developed, maintained, or supported
1. Documentation is available, such as a project website
1. Free of charge

F-Droid publishes useful [guidance on anti-features](https://f-droid.org/docs/Anti-Features/).

Entries are sorted alphabetically.

## F-Droid links

If a package is available on [**F-Droid**](https://f-droid.org/), link it using the `https://f-droid.org/packages/<App ID>` URL.
If it isn't listed yet, consider suggesting an F-Droid submission to the project's developers.

Link [**IzzyOnDroid**](https://apt.izzysoft.de/fdroid/) packages using `https://apt.izzysoft.de/packages/<App ID>` only when they aren't marked with *NonFreeComp*.

If the package is available on both, link F-Droid first, IzzyOnDroid second.

After adding or changing store links, run `python trust_metadata.py` and review
the generated `catalog-trust.json` entry for anti-features, sensitive permissions,
last update date, source archive availability, and reproducible-build status before
submitting the catalog change.

For apps mainly distributed outside Google Play, prefer upstream links that document
APK signing, release channels, F-Droid/IzzyOnDroid package availability, or Android
developer-verification status. This helps users in regions where certified Android
devices enforce developer verification starting September 30, 2026.

Before submitting README catalog changes, run `python contributor_check.py`. It checks
changed entries for source URL shape, metadata evidence, blocked anti-features, and
source health without requiring maintainers to inspect every field manually.

*Examples:*

```markdown
# Project page only: <Project>
* [**Example Project**](https://github.com/example/proj)

# F-Droid only: <Project> <F-Droid>
* [**Example Project**](https://github.com/example/proj) <sup>**[[F-Droid](https://f-droid.org/packages/ex.ample.proj)]**</sup>

# IzzyOnDroid only: <Project> <IzzyOnDroid>
* [**Example Project**](https://github.com/example/proj) <sup>**[[IzzyOnDroid](https://apt.izzysoft.de/packages/ex.ample.proj)]**</sup>

# F-Droid and IzzyOnDroid: <Project> <F-Droid> <IzzyOnDroid>
* [**Example Project**](https://github.com/example/proj) <sup>**[[F-Droid](https://f-droid.org/packages/ex.ample.proj)] [[IzzyOnDroid](https://apt.izzysoft.de/packages/ex.ample.proj)]**</sup>
```

Please don't submit links to other third-party F-Droid repositories or the Google Play Store.
