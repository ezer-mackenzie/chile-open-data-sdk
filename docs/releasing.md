# Release process

Publication is not automatic. The current workflow only prepares artifacts on
manual dispatch; it does not upload to PyPI or create a remote release.

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
maintainer access, and the intended publication account. Configure trusted
publishing and an appropriately protected environment if adopting that workflow.
Review the API, documentation, release notes, and any validation limitations.
Obtain explicit publication authorization before uploading or pushing release tags.

After approval, publish the reviewed artifacts, push the annotated tag, and create
release notes from `docs/release-notes.md`. Do not replace an already published
version or move an existing release tag. Fix genuine defects in a new patch
release. Signing is optional unless already configured reliably.

## Scope boundary

v0.1.0 is the synchronous foundation. Later roadmap features are not blockers for
this milestone. A 1.0 release requires a separate stable API review, complete
sync/async parity, and the broader validation described by the roadmap.
