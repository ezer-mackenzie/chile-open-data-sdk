# Compatibility and limitations

## Supported foundation

- Python 3.11, 3.12, 3.13, and 3.14 are the CI targets.
- Default endpoint: `https://datos.gob.cl/api/3/action`, without locale prefixes.
- Other CKAN sites can be configured, including deployment prefixes.
- Generic JSON POST Action API requests with explicit token authentication.
- Pydantic v2 validates envelopes, accepting extension fields and dynamic results.
- HTTPX 0.28.1 and Pydantic 2.12.0 are the declared minimum runtime versions;
  the CI minimum-dependency job tests these separately from the lockfile.

The contract follows the [CKAN v3 API documentation](https://docs.ckan.org/en/2.11/api/).
This does not certify every CKAN release, plugin, or portal. No upstream CKAN
version is inferred from the hostname. Live test findings are recorded in the
[release validation record](release-validation.md).

## v0.1.0 limitations

This release does not expose `datasets`, `resources`, `organizations`, `groups`,
`tags`, or `datastore` services, nor an asynchronous client. It provides no
pagination iterators, automatic retry/backoff, Retry-After handling, downloads,
file uploads, dataframe extras, SQL validation, or custom record adapters.

The generic API can reach catalog/DataStore/write actions if enabled on the server.
Responses remain JSON values and callers manage parameters and pagination.
Successful data is not redacted or reinterpreted. Unsupported actions may return
404 or CKAN API errors. No write permission or DataStore SQL support is assumed.

Redirects are disabled. A portal redirect results in `CKANHTTPError`; configure
the canonical trusted site explicitly if required. Environment proxy/netrc
configuration is not used. The client supports JSON actions only.

## Stability and migration

v0.1.0 is an alpha foundation, not a stable 1.x API contract. Breaking changes
before 1.0 must be described in the changelog. Typed high-level workflows will be
added in later milestones. The previous repository skeleton had no implemented
SDK; the supported import is now `chile_open_data`, replacing the empty
`chile_open_data_sdk` placeholder. Development moves from Poetry to uv and the
minimum Python version moves from 3.14 to 3.11.
