# Release process

The `Publish Python Package to PyPI` workflow validates, builds, and publishes
through PyPI Trusted Publishing. Publishing a non-prerelease GitHub Release
triggers it automatically. You can also run it manually with the required `tag`
input, naming an existing version tag (for example `v0.1.0`). Manual dispatch is a
publication action, not a build-only preview; it may also explicitly select a
prerelease tag if the package version and all checks agree.

The build job checks out `refs/tags/<tag>` with full history, verifies that the tag
is `v<project.version>` and resolves to the checked-out commit, then runs tests,
Ruff, mypy, BasedPyright, strict documentation, and artifact checks using uv.
Only after that job succeeds does a separate job download the built artifacts
and upload them to PyPI. Runs for the same tag share a concurrency group and do
not cancel an in-progress publication.

## Prepare a reviewable checkpoint

1. Inspect `git status` and recent history. Preserve existing user changes.
2. Keep the version synchronized in `pyproject.toml`, `__init__.py`, the default
   user agent, artifact checks, and version-specific installation examples.
3. Update CHANGELOG, release notes, compatibility limits, and the validation record.
4. Run the checks below and inspect the diff. Never tag a failing checkpoint.
5. Commit coherent work using Conventional Commits and approved coauthor trailers.
6. Create one annotated local tag only after all intended files are committed:
   `git tag -a v0.1.0 -m "chile-open-data-sdk v0.1.0"`.

```console
uv sync --locked --group docs
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run basedpyright
uv run pytest
uv run --group docs mkdocs build --strict
uv build
uv run python scripts/check_artifacts.py
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file .cache/requirements-audit.txt
uv run pip-audit -r .cache/requirements-audit.txt
```

Install the wheel and sdist into separate fresh virtual environments and import
`chile_open_data_sdk` from outside the checkout. The CI build job demonstrates this.
Run supported Python versions and the declared minimum dependencies as configured
in CI. Review the audit findings rather than ignoring advisory IDs without cause.

Run the opt-in read-only integration test when possible, recording endpoint,
date, and result. Upstream downtime must not be disguised as compatibility proof.
Review tracked files and Git history for accidental credentials; do not include
raw credentials in reports. Confirm the MIT license remains appropriate.

## Before any public release

Review the actual GitHub CI results for the release commit; local checks do not
prove remote CI has run. Confirm the package name is available/owned on PyPI,
maintainer access, and the intended publication account. Configure a PyPI Trusted
Publisher for the following identity:

- Project: `chile-open-data-sdk`.
- GitHub owner: `ezer-mackenzie`.
- Repository: `chile-open-data-sdk`.
- Workflow filename: `publish.yml`.
- GitHub environment: `pypi`.

Create/configure the `pypi` GitHub environment and any desired protection rules.
Only the publication job has `id-token: write`; no stored PyPI token is required.
See [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
Review the API, documentation, release notes, and any validation limitations
before publishing a GitHub Release or manually dispatching this workflow.

Push the reviewed annotated tag, then publish its GitHub Release with notes from
`docs/release-notes.md`, or manually dispatch `publish.yml` with that existing tag.
A tag push alone does not trigger this publishing workflow. Do not replace an
already published version or move an existing release tag. Fix genuine defects
in a new patch release. Signing is optional unless already configured reliably.

The existing local `v0.1.0` tag predates the import migration and these workflow
changes. Selecting it builds that historical source, not current `main`. This task
does not retag or publish it; settle the intended release commit before publishing.

## Scope boundary

v0.1.0 is the synchronous foundation. Later roadmap features are not blockers for
this milestone. A 1.0 release requires a separate stable API review, complete
sync/async parity, and the broader validation described by the roadmap.
