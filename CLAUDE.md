# Claude repository guide

Read and follow [AGENTS.md](AGENTS.md), the canonical repository instructions for
coding agents. Apply them together with the user's current request. Keep shared
rules there so the two guides do not drift.

## Working context

The distribution is `chile-open-data-sdk`; the Python package is
`chile_open_data_sdk`. The v0.2.0 milestone implements typed catalog discovery and dataset pagination
on top of synchronous generic CKAN actions.
Public clients, services, envelopes, response helpers, validators, JSON aliases,
and exceptions are available from the package root and their documented modules.
Shared defaults and immutable error mappings live in `constants.py`.

Use the repository `.venv` and locked uv tooling. Read `pyproject.toml` and
`pyrightconfig.json` before changing tool configuration. Preserve unrelated edits.
Run Ruff, format checking, mypy, BasedPyright, and offline pytest for code changes;
run strict MkDocs and artifact validation for docs and packaging changes.
The complete commands and optional benchmark setup are in AGENTS.md.

## Where to look

- [API reference](docs/api.md): supported exports and lower-level usage.
- [Architecture](docs/architecture.md): ownership and module responsibilities.
- [Development](docs/development.md): tooling and optional benchmark groups.
- [Contributing](CONTRIBUTING.md): validation and commit conventions.
- [Release process](docs/releasing.md): versioning and PyPI workflow.

Keep repository content in English and communicate in the user's language.
Describe completed changes and actual checks; clearly identify remaining work.
