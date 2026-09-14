# Error handling

Import exceptions from `chile_open_data_sdk.errors`. `ChileOpenDataError` is the root;
`CKANError` adds `action`, optional `status_code`, optional `error_type`, and
sanitized `details`. The message is intentionally stable and does not echo raw
server response bodies. Raw HTTPX requests/responses are not attached.

| Exception | Meaning |
| --- | --- |
| `CKANAPIError` | CKAN returned `success=false` |
| `CKANProtocolError` | Invalid JSON/envelope, missing result, or non-finite result |
| `CKANHTTPError` | Non-2xx response, including redirects |
| `CKANAuthenticationError` | HTTP 401 or CKAN Authentication Error |
| `CKANAuthorizationError` | HTTP 403 or CKAN Authorization Error |
| `CKANNotFoundError` | HTTP 404 or CKAN Not Found Error |
| `CKANValidationError` | HTTP 400/409/422 or CKAN Validation Error |
| `CKANRateLimitError` | HTTP 429 |
| `CKANTimeoutError` | HTTPX connect/read/write/pool timeout |
| `CKANConnectionError` | Other HTTPX request/transport failure |

Authentication, authorization, not-found, validation, and rate-limit exceptions
inherit from both `CKANAPIError` and `CKANHTTPError`, allowing category catches
regardless of whether a server uses HTTP status codes or a failure envelope.
Known HTTP status mappings take precedence over CKAN error types. Unknown CKAN
errors retain their type and sanitized payload. Unknown non-2xx statuses use
`CKANHTTPError`. A successful HTTP status never overrides `success=false`.

```python
from chile_open_data_sdk import ChileOpenDataClient
from chile_open_data_sdk.errors import CKANError, CKANNotFoundError

try:
    with ChileOpenDataClient() as client:
        result = client.actions.call("package_show", {"id": "missing-dataset"})
except CKANNotFoundError:
    print("Dataset not found")
except CKANError as error:
    print(error.action, error.status_code, error.error_type)
```

Configured token occurrences and credential-like keys are redacted recursively
in SDK error details, including nested lists and mapping keys. Successful result
data is preserved and may itself contain sensitive data; do not log it blindly.
Malformed/non-JSON response bodies are discarded from diagnostics.

Local configuration, invalid action names, and non-JSON parameters raise
`ValueError`. Calling a closed client raises `CKANError`. No exception triggers
an automatic retry in v0.2.0.
