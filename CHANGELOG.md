# Changelog

All notable changes are documented here. Versions before 1.0 may evolve their
public API; compatibility changes will be recorded explicitly.

## Unreleased

## 0.2.0

Prepared locally; publication and remote release validation are separate steps.

### Added

- Typed Dataset, Resource, Organization, Group, Tag, and DatasetSearchResult models
  that preserve extension fields, string IDs, dates, and resource URLs.
- Dataset listing, search, metadata lookup, and resource metadata lookup through
  dedicated services sharing the existing connection pool.
- Organization, group, and tag discovery with consistent list/get methods.
- Lazy dataset iter_pages and iter_search with configurable page size, initial
  offset, stable default ordering, and an optional item limit.
- Pagination handling for server page caps, empty pages, changing counts, and
  repeated pages; typed result failures use sanitized SDK protocol errors.
- Catalog guide, typed quick start, offline contracts, and opt-in live discovery tests.

### Changed

- Remove redundant module-level __all__ lists; retain the package-root list for
  typed convenience reexports. Explicit named module imports remain supported.
- Synchronize package version, user agent, lockfile, CI installation checks, and
  release documentation for 0.2.0. Artifact checks read the declared version.

## Foundation follow-up

### Changed

- Replace `_internal.responses` with public `responses` and `models` modules.
  Export services, helpers, validators, models, JSON aliases, and exceptions at
  the package root. Move defaults and immutable error maps to `constants`.
  Direct parser calls now redact configured tokens from diagnostic action names.
  Previous private imports must migrate; no private-path alias is retained.

- Rename the import package from `chile_open_data` to `chile_open_data_sdk` before
  publication. Update imports, documentation, CI, coverage, and artifact validation.
  The distribution remains `chile-open-data-sdk`; class names and behavior are unchanged.
  No compatibility alias is provided.

### Added

- Repository agent guides in AGENTS.md and CLAUDE.md and expanded public API reference.

- Optional BenchCore 1.x integration for Python 3.12+, with two explicitly selected
  CPU benchmarks, JSON report persistence, and a manual reports workflow. SDK and
  default development support remain Python 3.11+.

- Strict BasedPyright checks shared with Pyright/Pylance, enforced in CI.
- Local pre-commit hooks for Ruff, formatting, mypy, BasedPyright, and offline tests.
- Hypothesis property tests for arbitrary JSON results and immutable secret redaction.
- Optional pytest-benchmark group with network-free response and redaction benchmarks.
- Additional Ruff rules for security, comprehensions, logging, datetime usage, and debugging.

### Fixed

- Restore PyPI Trusted Publishing on published non-prerelease GitHub Releases and
  manual dispatch with a required existing tag. Verify tag/version/commit identity
  and run uv quality, documentation, and build checks before the isolated OIDC upload.

- Remove unnecessary-isinstance diagnostics by separating runtime validation of
  untyped configuration values from the typed configuration model.
- Make response assignment and quick-start JSON narrowing explicit for static analyzers.

These entries record foundation follow-up work. Inspect Git history and each tag
to identify the exact source included in a release.

## 0.1.0

Initial foundation release, prepared locally; publication is a separate step.

### Added

- Reusable synchronous `CKANClient` and Chile-first `ChileOpenDataClient`.
- Frozen typed configuration, granular timeouts, connection limits, TLS verification.
- Generic JSON Action API calls with unwrapped recursive JSON results.
- Pydantic v2 envelope validation and structured HTTP, CKAN, and transport errors.
- Explicit Authorization token support and recursive diagnostic redaction.
- Deterministic contract tests and an opt-in read-only portal test.
- English usage guides, generated API reference, policies, roadmap, and release notes.
- uv lockfile, typed package marker, Python 3.11–3.14 CI, build and artifact checks.

### Changed

- Replace the empty `chile_open_data_sdk` import skeleton with `chile_open_data`.
- Replace Poetry packaging with uv/uv_build and lower required Python from 3.14 to 3.11.
- Replace the inherited publishing workflow with manual artifact preparation.

### Security

- Disable redirects, environment credentials/proxies, and automatic request replay.
- Exclude configured tokens and raw HTTP response bodies from SDK diagnostics.
