# Getting started

Install the local project using `uv sync --locked`. See the repository README for
wheel installation and the command to use after publication. Python 3.11–3.14
are the supported test targets.

## First request

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    result = client.datasets.search("transport", rows=5)
    for dataset in result.results:
        print(dataset.title)
```

Use a context manager to release pooled connections. For long-lived applications,
create one client, reuse it, and call `client.close()` during shutdown. Closing is
idempotent. A closed client cannot be reused; create a new one.

Typed catalog services return models; see [Catalog discovery](catalog.md).
For `client.actions.call`, the Action API envelope is checked before returning `result`. JSON null becomes
`None`, and lists, dictionaries, strings, numbers, and booleans retain their JSON
meaning. No dataset model is implied by a generic result. Use `isinstance` checks
when narrowing the recursive `JSONValue` type.

Requests can raise SDK errors, including when HTTP is successful but CKAN reports
`success=false`. See [errors](errors.md).

The runnable example is `examples/quickstart.py`; from the checkout run
`uv run python examples/quickstart.py`. This contacts the live portal and may fail
when the upstream service is unavailable. Its request and output logic are also
tested offline with a mock transport.
