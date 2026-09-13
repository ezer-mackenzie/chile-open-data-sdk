# v0.1.0 release notes

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
replace `chile_open_data` imports with `chile_open_data_sdk`. The original local
v0.1.0 tag predates this migration and remains unchanged; these notes describe the
current pre-publication source.

## Known limitations

No typed catalog/DataStore services, pagination helpers, async client, downloads,
file uploads, dataframe integrations, or retry policy are included yet. Generic
actions remain available when upstream supports them. This is not a stable 1.x
API and is not an official government SDK.

Review the [validation record](release-validation.md) for the actual local results
and any release prerequisites. PyPI publication and remote tags are separate,
explicit maintainer actions.
