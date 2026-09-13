# Contributing

Thank you for helping improve this unofficial community SDK. Keep repository
code, documentation, examples, and commit messages in English. Spanish is allowed
in upstream data and examples demonstrating Chilean data.

## Set up

Install Python 3.11+ and uv, clone the repository, then run:

```console
uv sync --locked --group docs
```

Use `uv add`, `uv add --dev`, or `uv add --group docs` to change dependencies.
Never hand-edit `uv.lock`. Runtime dependencies should be justified by features;
optional integrations must remain optional. No global Python tooling is required.

## Validate before each commit

```console
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

For documentation and packaging changes, also run:

```console
uv run --group docs mkdocs build --strict
uv build
uv run python scripts/check_artifacts.py
```

Tests use HTTPX MockTransport by default and enforce 90% branch-aware coverage.
Add behavior-focused tests for public changes and credential-sensitive paths.
Never test writes against production. To explicitly enable public read tests:

```powershell
$env:CHILE_OPEN_DATA_LIVE_TESTS = "1"
uv run pytest tests/integration --no-cov
```

On POSIX shells use `CHILE_OPEN_DATA_LIVE_TESTS=1 uv run pytest tests/integration --no-cov`.
Live availability is not a normal pull-request requirement.

## Changes and review

Keep changes coherent and follow the roadmap. Describe the problem, resulting
behavior, compatibility impact, and validation in pull requests. Update docs and
CHANGELOG for user-visible changes. Use Conventional Commits such as
`feat(core): ...`, `fix(actions): ...`, and `docs(api): ...`.

Do not manufacture release history, rewrite user commits, or force-push. For
agent-assisted changes, include an approved `Co-authored-by` identity; never
invent one. Public API stability begins at 1.0, not at this alpha milestone.

Report security issues through [SECURITY.md](SECURITY.md). Participation follows
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
