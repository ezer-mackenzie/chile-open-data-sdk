# Development tools

All tools are managed by uv and locked in `uv.lock`. They do not become runtime
dependencies of the published SDK. Run `uv sync --locked --group docs` after pulling
changes. Use the project's `.venv` interpreter in your editor.

| Tool | Purpose | Command |
| --- | --- | --- |
| Ruff | Lint, import ordering, and formatting | `uv run ruff check .` / `uv run ruff format .` |
| mypy | Strict SDK typing | `uv run mypy src` |
| BasedPyright | Strict SDK, example, and build-script typing | `uv run basedpyright` |
| pytest / pytest-cov | Offline behavior tests and branch coverage | `uv run pytest` |
| Hypothesis | Generated JSON and redaction invariants | Included in normal pytest |
| pre-commit | Run checks before committing | `uv run pre-commit install` |
| pip-audit | Known dependency vulnerabilities | See the release guide |
| pytest-benchmark | Optional local CPU measurements | See below |

## Type validation and editor diagnostics

`pyrightconfig.json` is shared by BasedPyright and Pyright/Pylance. It selects
Python 3.11-compatible syntax and strict checks for `src`, `examples`, and
`scripts`. Tests deliberately exercise invalid runtime inputs and are executed
with pytest rather than included in this strict static-analysis scope.

`reportUnnecessaryIsInstance` remains an error. Do not silence it globally or remove
runtime validation just to satisfy the editor. An annotated `int` can still receive
a string from untyped caller code. The configuration validators accept `object`
at that boundary, narrow actual runtime values, and reject booleans as connection
counts. Typed configuration fields retain their precise public annotations.

JSON narrowing uses a local variable for dictionary lookup results so analyzers
can prove the value being iterated is a list. The transport's `try/except/else`
structure makes successful response assignment explicit and still avoids retaining
raw HTTP exceptions in credential-bearing diagnostic chains.

If the editor reports unresolved imports, select `.venv` and restart its language
server after `uv sync`; do not disable missing-import or type diagnostics.

## Ruff and commit hooks

The rule set covers errors, imports, modern syntax, common bugs, comprehensions,
timezone mistakes, logging, redundant code, debugger statements, and security
patterns. Assertions and synthetic credentials are allowed specifically in tests
and benchmarks; production security checks remain enabled.

Run `uv run pre-commit install` once per clone, then use
`uv run pre-commit run --all-files` to check the full project. Hooks run local uv
commands using locked dependencies. Formatting is checked without rewriting files;
use `uv run ruff format .` to apply it. Hooks include offline pytest and therefore
also enforce the coverage floor. Live portal tests remain explicitly opt-in.

## Property tests

Hypothesis generates nested, finite JSON values to check that CKAN response
unwrapping preserves their structure. It also checks that diagnostic redaction
removes nested credentials, does not mutate the input, and is idempotent. Saved
failing examples live in the ignored `.hypothesis/` directory.

## Benchmarks

The optional `benchmark` dependency group installs pytest-benchmark. Benchmarks
are outside pytest's normal `tests/` discovery and make no network requests:

```console
uv run --group benchmark pytest benchmarks --no-cov --benchmark-only
uv run --group benchmark pytest benchmarks --no-cov --benchmark-only --benchmark-autosave
uv run --group benchmark pytest benchmarks --no-cov --benchmark-only --benchmark-compare
```

The two cases measure parsing a 1,000-row response and redacting 100 nested error
entries. Coverage is disabled for timing measurements. Baselines are local to the
machine and stored in ignored `.benchmarks/`; compare on the same machine and
interpreter under similar load. These are observations, not performance promises
or fixed CI timing gates. Normal CI does not run the benchmark group.

References: [Ruff rules](https://docs.astral.sh/ruff/rules/),
[BasedPyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/),
[Hypothesis](https://hypothesis.readthedocs.io/en/latest/quickstart.html),
[pre-commit](https://pre-commit.com/), and
[pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/usage.html).
