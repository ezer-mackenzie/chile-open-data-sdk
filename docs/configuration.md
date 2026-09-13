# Configuration and authentication

`ClientConfig` is a frozen, typed dataclass. Pass it as `config=` to either client:

```python
from chile_open_data import ChileOpenDataClient, ClientConfig

config = ClientConfig(read_timeout=60.0, max_connections=20, max_keepalive_connections=10)
with ChileOpenDataClient(config=config) as client:
    result = client.actions.call("package_list", {"limit": 5})
```

| Setting | Default | Meaning |
| --- | --- | --- |
| `site_url` | `https://datos.gob.cl` | HTTP(S) site, optionally with deployment prefix |
| `action_path` | `/api/3/action` | Absolute action path appended to the site |
| `api_token` | `None` | Explicit CKAN Authorization value, excluded from repr |
| `user_agent` | `chile-open-data-sdk/0.1.0` | Request user agent |
| `connect_timeout` | `5.0` | Connect timeout in seconds |
| `read_timeout` | `30.0` | Read timeout in seconds |
| `write_timeout` | `30.0` | Write timeout in seconds |
| `pool_timeout` | `5.0` | Pool acquisition timeout in seconds |
| `max_connections` | `100` | Maximum pooled connections |
| `max_keepalive_connections` | `20` | Maximum idle reusable connections |
| `verify` | `True` | TLS certificate verification |

Timeouts must be finite and positive. Limits must be integers with
`0 <= max_keepalive_connections <= max_connections` and `max_connections >= 1`.
Trailing slashes are normalized. Site URLs reject embedded credentials, queries,
fragments, traversal segments, and encoded path segments. Invalid configuration
raises `ValueError` without echoing its values. Header values must be printable
ASCII and nonempty when supplied.

`CKANClient(site_url=...)` requires an explicit site or config. The Chile client
supplies the Chilean default and accepts a site override. Use either `config` or
the `site_url`/`api_token` convenience arguments, never both.

## Credentials

Public reads normally need no token. For authenticated actions, obtain a token
from the target CKAN instance and pass it explicitly. A token does not grant
permissions beyond those assigned by the server.

```python
import os
from chile_open_data import ChileOpenDataClient

with ChileOpenDataClient(api_token=os.environ["CHILE_OPEN_DATA_API_TOKEN"]) as client:
    result = client.actions.call("package_list", {"limit": 5})
```

This environment lookup belongs to your application. The standard constructors
never load credentials implicitly; there is no `from_env()` helper in v0.1.0.

Redirects are always disabled and surface as HTTP errors. Environment proxy and
netrc settings are ignored (`trust_env=False`). Proxy configuration is not exposed
in v0.1.0. Use HTTPS for credentials; HTTP support exists for local CKAN deployments.
The SDK does not log tokens or retain raw HTTPX requests in its exceptions. An
application that inspects config fields, enables external HTTP debugging, or logs
its own input is responsible for protecting those values.

A custom `httpx.BaseTransport`, including `MockTransport`, may be injected with
`transport=`. The SDK owns and closes it. Custom transports control their own
network behavior; do not share one transport across clients with separate lifetimes.
