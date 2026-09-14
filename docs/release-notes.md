# v0.2.0 release notes

This alpha adds typed catalog discovery and dataset pagination. It retains the
synchronous client, generic Action API, explicit authentication, and existing
exception hierarchy. Python 3.11 through 3.14 remain supported.

## New capabilities

- `client.datasets.list`, `search`, and `get` for dataset discovery and metadata.
- `client.resources.get` for resource metadata without downloading data.
- `client.organizations`, `client.groups`, and `client.tags` with list/get methods.
- Pydantic catalog models with typed nested resources and preserved plugin fields.
- Lazy `datasets.iter_pages` and `datasets.iter_search`, configurable page sizes,
  stable default sorting, and optional item limits for item iteration.
- Safe SDK protocol errors for malformed typed responses and repeated pages.

Search accepts q, fq, sort, rows, start, and explicit extra parameters without
rewriting query semantics. Pagination advances by returned rows, supports server
page caps, and stops at an empty page or the first page's total count. Offset
paging cannot guarantee a consistent snapshot during concurrent catalog edits.

## Migration

The package remains `chile_open_data_sdk`. Existing generic actions still return
JSON values. Use the typed services when their models fit your workflow.

Redundant `__all__` declarations were removed from individual modules; the root
package retains its explicit reexport contract. Named public imports remain
supported. Prefer named imports over wildcard imports.

Earlier private response imports must use `chile_open_data_sdk.responses` and
`chile_open_data_sdk.models`. See the [API reference](api.md) and
[catalog guide](catalog.md) for the public surface and examples.

## Remaining milestones

Typed DataStore reads/SQL and record iteration target v0.3.0. Async clients,
retries, authenticated write services, downloads, and dataframe integrations are
later work. This alpha is not a stable 1.x API or an official government SDK.

The source and distributions are prepared locally. Publication requires the
[release process](releasing.md); local checks do not prove remote CI or PyPI status.
Historical foundation notes are retained below.

---

## Historical v0.1.0 foundation notes

This first alpha delivers the reusable CKAN foundation for a Chile-first SDK.
Use `ChileOpenDataClient` for datos.gob.cl or `CKANClient(site_url=...)` for another
compatible site, and call `client.actions.call(...)` with JSON parameters.

The client reuses connections, validates CKAN envelopes, unwraps results, and maps
HTTP/CKAN/transport failures into SDK exceptions. Configuration includes explicit
tokens, granular timeouts, connection limits, and TLS verification. SDK diagnostic
context redacts credentials. Generic requests are never automatically retried or
redirected.

## Compatibility and migration

Python 3.11–3.14 are the test targets. The import is `chile_open_data_sdk`, while the
distribution remains `chile-open-data-sdk`. The repository's former empty package
and Poetry configuration are replaced by a uv-managed `src/` package. There is no
previous published SDK API to migrate. If using an earlier local checkout,
replace `chile_open_data` imports with `chile_open_data_sdk`. These notes describe the current source; inspect the selected release tag
to confirm which changes it includes.

Response parsing, redaction, envelope models, validators, services, and exceptions
are public APIs with package-root exports. Shared constants and JSON aliases live
in dedicated modules. Earlier `_internal.responses` imports must migrate to
`chile_open_data_sdk.responses`; `ActionResponse` lives in `models`.
Repository agent guidance is documented in AGENTS.md and CLAUDE.md.

## Known limitations

No typed catalog/DataStore services, pagination helpers, async client, downloads,
file uploads, dataframe integrations, or retry policy are included yet. Generic
actions remain available when upstream supports them. This is not a stable 1.x
API and is not an official government SDK.

Review the [validation record](release-validation.md) for the actual local results
and any release prerequisites. PyPI publication and remote tags are separate,
explicit maintainer actions.
