# Generic actions

`client.actions.call(action, data=None)` sends a JSON object in an HTTP POST to
`<site_url><action_path>/<action>`. Parameters are not transformed into a custom
query language. Nested mappings, lists, booleans, and null are encoded as JSON.
Action names must start with an ASCII letter and contain only ASCII letters,
digits, and underscores. Files and multipart uploads are not supported.

The return type is `JSONValue`: null, boolean, integer, float, string, list, or
string-keyed dictionary, recursively. Parameters must also be JSON-compatible,
with finite numeric values. Unknown CKAN result fields are preserved.

## Catalog queries available through the generic API

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    names = client.actions.call("package_list", {"limit": 5})
    search = client.actions.call(
        "package_search",
        {
            "q": "transport",
            "fq": "res_format:CSV",
            "rows": 5,
            "start": 0,
        },
    )
    organizations = client.actions.call("organization_list", {"limit": 5})
```

`package_show` and `resource_show` accept an `id` parameter supplied by your
application. The names and capabilities of actions depend on the CKAN server and
its plugins. Prefer the planned typed services when they become available.

## DataStore examples

The following assumes an existing client and a resource ID obtained from dataset
metadata. These are generic calls, not the future typed DataStore service:

```python
result = client.actions.call(
    "datastore_search",
    {
        "resource_id": resource_id,
        "filters": {"region": "Metropolitana"},
        "fields": ["region"],
        "limit": 10,
        "offset": 0,
    },
)
```

Field names and filter values must match the resource. `datastore_search_sql` can
be called with `{"sql": sql}` if enabled upstream. SQL is caller-provided: never
build it from untrusted input without proper validation. The SDK does not sanitize
SQL or implement an ORM. DataStore availability is not guaranteed.

## Writes, pagination, and retry policy

The generic escape hatch can invoke authenticated write actions. There is no
read-only allowlist or write confirmation in the SDK. CKAN enforces authorization.
Never use production writes as connectivity tests.

Every call makes one attempt. A timeout can occur after a write was applied; do
not blindly repeat it. Pagination is manual in v0.1.0: set `start`/`rows` or
`offset`/`limit` as appropriate. No background or unbounded fetching occurs.

Protocol references: [CKAN Action API](https://docs.ckan.org/en/2.11/api/) and
[DataStore API](https://docs.ckan.org/en/2.11/maintaining/datastore.html).
