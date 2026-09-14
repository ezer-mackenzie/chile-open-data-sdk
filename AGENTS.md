# Repository instructions for coding agents

## Project and scope

This repository builds `chile-open-data-sdk`; Python imports use
`chile_open_data_sdk`. It is an unofficial Chile-first CKAN Action API SDK.
The v0.2.0 SDK includes synchronous typed catalog services and dataset pagination,
built on HTTPX and Pydantic v2.
Follow `docs/roadmap.md`; async clients, retries, DataStore services, and dataframe
integrations belong to later milestones unless explicitly requested.

Keep code, documentation, examples, and commit messages in English. Respond to
the user in their preferred language. Preserve Spanish in upstream data.

## Layout and public API

- `src/chile_open_data_sdk/client.py`: clients and `ActionService`.
- `catalog.py`: dataset, resource, organization, group, and tag services.
- `config.py`: immutable validated `ClientConfig`.
- `constants.py`: shared defaults, patterns, and read-only error mappings.
- `types.py`: recursive JSON aliases; `models.py`: Pydantic envelopes and catalog models.
- `responses.py`: public parsing and diagnostic redaction.
- `validation.py`: public runtime validators; `errors.py`: exception hierarchy.
- `__init__.py`: supported convenience exports and package version.
- `tests/`: offline unit/property tests and opt-in integration tests.
- `benchmarks/`: optional CPU benchmarks; `docs/`: MkDocs documentation.
- `scripts/check_artifacts.py`: wheel and sdist validation.

Expose reusable SDK functionality through public modules and document its
contract in `docs/api.md`. Keep shared constants and types in their owning modules.
Use `__all__` only at the package root to declare convenience reexports; avoid
redundant lists in individual modules. Do not reintroduce an `_internal` package. Keep per-instance implementation state
encapsulated and respect HTTP client ownership. Update exports, examples, tests,
and compatibility notes together when changing a public API.

## Environment and checks

Use Python 3.11+ and uv. Start with `uv sync --locked --group docs`.
Use `uv add` for dependency changes; never hand-edit `uv.lock`. Keep development,
documentation, and benchmark dependencies outside runtime requirements.

Before committing code, run:

```console
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run basedpyright
uv run pytest
```

For documentation or packaging changes, also run:

```console
uv run --group docs mkdocs build --strict
uv build
uv run python scripts/check_artifacts.py
```

Use `uv run ruff format .` to format intentionally. Preserve strict typing and the
unnecessary-isinstance diagnostic. Validate untrusted runtime values through
object-typed boundaries instead of disabling diagnostics or deleting safeguards.
Write behavior-focused tests with HTTPX MockTransport. Normal tests must work
without network access and meet the configured coverage threshold.

Optional benchmarks:

```console
uv run --group benchmark pytest benchmarks --no-cov --benchmark-only
uv run --group benchcore pytest benchmarks/benchcore_cases.py --no-cov --benchcore-save=.benchcore
```

BenchCore requires Python 3.12+. Live read tests require explicit opt-in through
`CHILE_OPEN_DATA_LIVE_TESTS=1`. Never issue test writes against production.

## Behavioral and security contracts

Reuse connections, close owned transports, and preserve context-manager behavior.
Do not add implicit environment credentials, automatic retries, redirects, global
logging configuration, or event-loop creation to synchronous calls. Keep TLS
verification enabled by default. Do not expose tokens through repr, diagnostics,
exception chains, fixtures, or reports. Successful result data is returned intact;
redaction applies to diagnostics and explicit calls to `redact`.

## Changes and releases

Inspect status and existing changes first. Preserve unrelated user edits and do
not stage them with your work. Keep commits coherent and use Conventional Commits.
Include the approved agent coauthor trailer for this repository:
`Co-authored-by: Codex <noreply@openai.com>`.

Update CHANGELOG and relevant documentation for user-visible changes. Report the
checks actually run and any remaining limitations. Do not invent validation,
publication status, or release history. Follow `docs/releasing.md` for releases;
keep `pyproject.toml` and `constants.SDK_VERSION` synchronized. The exported version
and default user agent derive from that constant. A code-edit request alone does
not authorize publication, pushing, or moving an existing release tag.

See `CONTRIBUTING.md`, `SECURITY.md`, and `docs/development.md` for further guidance.
