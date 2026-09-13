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
| pytest-benchmark | Optional local CPU measurements, Python 3.11+ | See below |
| BenchCore | Optional typed measurements and JSON reports, Python 3.12+ | See below |

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

### pytest-benchmark

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

### BenchCore

BenchCore 1.x is installed through a separate optional development group. It
requires Python 3.12 or later; this does not raise the SDK's Python 3.11 minimum.
uv rejects selecting this group with an incompatible interpreter rather than
silently leaving out the requested tool. The package wheel does not depend on
BenchCore or either benchmarking integration.

Run on Python 3.12+ in an isolated project environment if you want to preserve
your main development interpreter. For example, in PowerShell:

```powershell
$env:UV_PROJECT_ENVIRONMENT = ".cache/benchcore-env"
uv run --python 3.12 --group benchcore pytest benchmarks/benchcore_cases.py --no-cov --benchcore-save=.benchcore
Remove-Item Env:UV_PROJECT_ENVIRONMENT
```

With an existing Python 3.12+ development environment, simply run:

```console
uv run --locked --group benchcore pytest benchmarks/benchcore_cases.py --no-cov --benchcore-save=.benchcore
```

The two cases measure the same workloads as the pytest-benchmark suite, using
20 measured rounds, two warmup rounds, and 10 iterations per round. Setup happens
before measurement; assertions inspect `BenchmarkResult.value` after measurement.
There are no network calls, timing assertions, or performance release gates.

`benchcore_cases.py` is deliberately named outside pytest's `test_*.py` convention
and must be selected explicitly. Consequently ordinary tests and the existing
`pytest benchmarks --benchmark-only` command do not require BenchCore, even on
Python 3.11. Use the `BenchCoreFixture` fixture for these cases; BenchCore is not
a drop-in replacement for pytest-benchmark's `benchmark` fixture.

`--benchcore-save` writes schema-validated JSON reports into ignored `.benchcore/`.
Report identities include workload sizes. Save distinct output directories for
runs you want to compare; saving the same names in one directory replaces their
previous reports. Compare only compatible environments using BenchCore's report
comparison API; do not interpret a single timing difference as statistical proof.

The **BenchCore reports** GitHub Actions workflow runs only on manual dispatch
and uploads the JSON reports. It does not run on normal pull requests or publish
a release. Hosted runners vary in load, so those reports are diagnostic artifacts,
not a stable performance baseline. This workflow is configured locally; a remote
execution is a separate action.

References: [BenchCore 1.0.0](https://pypi.org/project/benchcore/1.0.0/),
[Ruff rules](https://docs.astral.sh/ruff/rules/),
[BasedPyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/),
[Hypothesis](https://hypothesis.readthedocs.io/en/latest/quickstart.html),
[pre-commit](https://pre-commit.com/), and
[pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/usage.html).
