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

## v0.2.0 limitations

This release includes `datasets`, `resources`, `organizations`, `groups`, and
`tags` services and lazy dataset search pagination. It does not provide typed
DataStore services, asynchronous clients, automatic retry/backoff, Retry-After
handling, downloads, file uploads, dataframe extras, SQL validation, or custom
record adapters. Organization/group lists are single pages. Tag lists follow the
upstream unpaginated action contract.

The generic API can reach catalog/DataStore/write actions if enabled on the server.
Responses remain JSON values and callers manage parameters and pagination.
Successful data is not redacted or reinterpreted. Unsupported actions may return
404 or CKAN API errors. No write permission or DataStore SQL support is assumed.

Redirects are disabled. A portal redirect results in `CKANHTTPError`; configure
the canonical trusted site explicitly if required. Environment proxy/netrc
configuration is not used. The client supports JSON actions only.

## Stability and migration

v0.2.0 is an alpha release, not a stable 1.x API contract. Breaking changes
before 1.0 must be described in the changelog. Further high-level workflows will be
added in later milestones. The supported import is `chile_open_data_sdk`, matching
the distribution name
`chile-open-data-sdk`. Earlier development snapshots
used `chile_open_data`; update all imports to `chile_open_data_sdk`, including
submodule imports such as `chile_open_data_sdk.errors`. No compatibility alias is
provided because this naming change occurs before publication. Class names and
behavior remain unchanged. Development uses uv and requires Python 3.11 or later.

Response utilities now live in the public `chile_open_data_sdk.responses` module.
Replace imports from `chile_open_data_sdk._internal.responses` with that path;
import `ActionResponse` from `chile_open_data_sdk.models` or the package root.
The private package has been removed without an alias. Shared constants and JSON
types are available in `constants` and `types`; see the [API reference](api.md).

Catalog models require string IDs and (except resources) names. Optional metadata
may be absent or null; arbitrary plugin fields are preserved. Dates and URLs stay
strings. Nonstandard schemas that omit identity fields remain accessible through
`actions.call`. Service-level schema errors become `CKANProtocolError` without
raw validation details or a status code; direct model validation raises Pydantic's
`ValidationError`. Search counts must be nonnegative integers, excluding booleans.

Only the root package defines `__all__`. Named imports from public modules remain
supported; wildcard imports from individual modules are not a compatibility contract.
