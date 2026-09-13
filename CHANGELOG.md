# Changelog

All notable changes are documented here. Versions before 1.0 may evolve their
public API; compatibility changes will be recorded explicitly.

## Unreleased

No changes yet.

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
