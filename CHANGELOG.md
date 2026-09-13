# Changelog

All notable changes are documented here. Versions before 1.0 may evolve their
public API; compatibility changes will be recorded explicitly.

## Unreleased

### Changed

- Rename the import package from `chile_open_data` to `chile_open_data_sdk` before
  publication. Update imports, documentation, CI, coverage, and artifact validation.
  The distribution remains `chile-open-data-sdk`; class names and behavior are unchanged.
  No compatibility alias is provided. The original local v0.1.0 tag is preserved.

### Added

- Strict BasedPyright checks shared with Pyright/Pylance, enforced in CI.
- Local pre-commit hooks for Ruff, formatting, mypy, BasedPyright, and offline tests.
- Hypothesis property tests for arbitrary JSON results and immutable secret redaction.
- Optional pytest-benchmark group with network-free response and redaction benchmarks.
- Additional Ruff rules for security, comprehensions, logging, datetime usage, and debugging.

### Fixed

- Remove unnecessary-isinstance diagnostics by separating runtime validation of
  untyped configuration values from the typed configuration model.
- Make response assignment and quick-start JSON narrowing explicit for static analyzers.

These changes follow the local v0.1.0 checkpoint; the existing tag is not moved.

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
