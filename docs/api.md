# API reference

All SDK modules below are public. Clients, `ActionService`, `ClientConfig`,
catalog models and services, `ActionResponse`, `JSONObject`, `JSONValue`, response helpers, runtime validators,
and all SDK exception classes can also be imported from `chile_open_data_sdk`.
`__version__` exposes the SDK version; shared constants are available through
`from chile_open_data_sdk import constants`.

## Using response helpers directly

```python
import httpx
from chile_open_data_sdk import JSONObject, parse_response, redact

payload: JSONObject = {"success": True, "result": {"count": 3}}
response = httpx.Response(200, json=payload)
result = parse_response(response, action="package_search")
safe_details = redact({"api_key": "example", "message": "public"})
```

`parse_response` accepts a fully read HTTPX response and performs no requests.
It returns the original JSON result, including explicit null, or raises an SDK
exception. HTTP status mappings take precedence over CKAN error type mappings;
unrecognized failures use `CKANHTTPError` or `CKANAPIError`. Invalid successful
envelopes, missing results, and non-finite results raise `CKANProtocolError`.
Pass `token` to remove a known credential from diagnostic actions and details.
Successful results are not redacted.

`redact` returns a recursive copy of lists and objects without changing the input.
It replaces the configured token in strings and keys and masks values whose keys
contain credential fragments, case-insensitively. It is not a general personal-data
anonymizer. The token defaults to None; credential-key masking still applies.

`ActionResponse` validates envelope structure with a strict boolean `success` and
preserves extension metadata. It does not enforce success, require a result, or
sanitize raw model contents; use `parse_response` for those response semantics.

## Clients and configuration

`client.actions` is the usual entry point. When constructing `ActionService`
directly, the caller owns and configures the supplied HTTPX client, including
headers, timeouts, redirects, and its lifetime; the service only executes actions.
`CKANClient` handles that configuration and ownership for normal usage.

::: chile_open_data_sdk.client.CKANClient

::: chile_open_data_sdk.client.ChileOpenDataClient

::: chile_open_data_sdk.client.ActionService

::: chile_open_data_sdk.config.ClientConfig

## Models, types, and response utilities

::: chile_open_data_sdk.models

::: chile_open_data_sdk.types

::: chile_open_data_sdk.responses

## Constants and runtime validation

Constants describe defaults; pass overrides to `ClientConfig`. Reassigning module
constants is not a supported way to configure a client. `HTTP_ERROR_TYPES` and
`CKAN_ERROR_TYPES` are read-only mappings. Timeout constants are seconds and
connection-limit constants are counts. Patterns are used with fullmatch.

`is_connection_limit` checks integer type while excluding booleans; range checking
belongs to `ClientConfig`. `validate_tls_verification` accepts only booleans and
raises ValueError otherwise. Both accept object inputs for runtime validation.

::: chile_open_data_sdk.constants

::: chile_open_data_sdk.validation

## Exceptions

::: chile_open_data_sdk.errors

## Catalog services

See [Catalog discovery](catalog.md) for parameter mappings, model tolerance,
pagination semantics, and complete usage examples. Services share the client's
`ActionService`; direct construction does not create or own an HTTP client.

::: chile_open_data_sdk.catalog.DatasetService

::: chile_open_data_sdk.catalog.ResourceService

::: chile_open_data_sdk.catalog.OrganizationService

::: chile_open_data_sdk.catalog.GroupService

::: chile_open_data_sdk.catalog.TagService
