# v0.1.0 release validation

Local verification performed on **2026-09-13**, on Windows x86-64 with uv 0.12.13.
This is evidence for the foundation milestone, not a claim that the future
catalog, DataStore, or async services already exist.

## Results

| Check | Result |
| --- | --- |
| `uv lock --check` | Passed; lockfile matches project dependencies |
| Ruff lint and format checks | Passed |
| Strict mypy on `src` | Passed, seven source files |
| Python 3.11.16 | 84 passed, one live test skipped by default |
| Python 3.12.14 | 84 passed, one live test skipped by default |
| Python 3.13.15 | 84 passed, one live test skipped by default |
| Python 3.14.7 | 84 passed, one live test skipped by default |
| Minimum runtime dependencies | 84 passed on Python 3.11 with HTTPX 0.28.1 and Pydantic 2.12.0 |
| Core coverage | 100% statements and branches in the measured suite; enforced floor 90% |
| Runnable quick start | Verified offline using a mock response |
| Live public portal read | Passed: JSON POST `package_search`, `rows=1`, no credentials |
| Strict MkDocs build | Passed |
| Wheel and source distribution | Built successfully using uv_build |
| Archive inspection | Import layout, metadata, MIT license, `py.typed`, source docs/tests verified |
| Isolated wheel installation | Import and client lifecycle passed from installed site-packages |
| Isolated sdist installation | Build, import, and client lifecycle passed from installed site-packages |
| Runtime dependency audit | pip-audit reported no known vulnerabilities in the locked runtime set |

The live check used `https://datos.gob.cl/api/3/action/package_search` and verified
an object with integer `count` and list `results`. No locale path, redirects,
authentication, writes, or fixed resource ID were required. This is a dated
connectivity/shape check, not a portal uptime or all-actions guarantee.

The default environment used HTTPX 0.28.1 and Pydantic 2.13.5. Separate minimum
version tests do not modify the committed lockfile. Artifact smoke checks used
Python's isolated mode and confirmed imports came from fresh environments, not
from the checkout. The sdist also includes documentation, examples, tests, and
`uv.lock`; caches and virtual environments are excluded.

Material for MkDocs printed an informational notice about its future MkDocs 2
compatibility. The installed MkDocs 1.6.1 documentation build passed strict mode.
No dependency advisory was suppressed.

A heuristic review of the eight reachable Git commits found one credential-like
URL: the intentional `user:pass` fixture in the invalid-URL test. No production
credential was identified by the reviewed patterns. This is not an exhaustive
secret-detection guarantee.

## Before publishing

- Review the GitHub Actions result for the exact release commit. The workflow is
  configured for Ubuntu/Python 3.11–3.14, but remote CI has not been run in this task.
- Confirm PyPI package ownership, publication account, and explicit authorization.
- Configure hosted documentation if desired; no public documentation deployment
  is claimed by the README.
- Review the alpha API, limitations, changelog, and release notes.

No PyPI upload, remote release, or tag push was performed. The local annotated
`v0.1.0` tag represents the reviewed source checkpoint only.
