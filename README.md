# Chile Open Data SDK

An unofficial, typed Python SDK for Chile's **datos.gob.cl**, with a reusable
CKAN Action API core. This community project is **not an official SDK of the
Government of Chile or the maintainers of datos.gob.cl**.

## v0.2.0 scope

This alpha adds typed dataset search and metadata lookup, resource metadata,
organization/group/tag discovery, and lazy catalog pagination to the synchronous
CKAN client. Configuration, connection pooling, explicit token authentication,
generic actions, and structured errors remain available.

DataStore wrappers, async clients, retries, downloads, and dataframe integrations
belong to later milestones. See the [catalog guide](docs/catalog.md).

## Installation

Python 3.11 or later is required. Before publication, install from a local checkout:

```console
uv sync --locked
```

Or build and install the wheel with a standard Python installer:

```console
uv build
python -m pip install dist/chile_open_data_sdk-0.2.0-py3-none-any.whl
```

After v0.2.0 is published, installation will be:

```console
python -m pip install chile-open-data-sdk==0.2.0
```

The distribution is `chile-open-data-sdk`; the import is `chile_open_data_sdk`.

## Quick start

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    result = client.datasets.search("transport", rows=5)
    for dataset in result.results:
        print(dataset.title)
```

The default endpoint is `https://datos.gob.cl/api/3/action`. Typed catalog calls return Pydantic models, while `client.actions.call` returns
the unwrapped JSON `result`. Both preserve additional server fields. Availability and
metadata quality depend on the upstream portal.

## Another CKAN site

```python
from chile_open_data_sdk import CKANClient

with CKANClient(site_url="https://demo.ckan.org") as client:
    print(client.actions.call("package_list", {"limit": 5}))
```

## Authentication and errors

Credentials are explicit and are sent only in the `Authorization` header. The
constructor does not read environment credentials. Your application can do so:

```python
import os

from chile_open_data_sdk import ChileOpenDataClient
from chile_open_data_sdk.errors import CKANError

try:
    with ChileOpenDataClient(api_token=os.environ.get("CHILE_OPEN_DATA_API_TOKEN")) as client:
        result = client.actions.call("package_list", {"limit": 5})
except CKANError as error:
    print(error.action, error.status_code, error.error_type)
```

Generic calls use JSON POST and **never retry automatically**, including read
operations. They can execute writes: the caller chooses the action and the server
enforces permissions. Redirects are not followed. Configuration and SDK error
representations exclude the configured token; do not log raw payloads or credentials.

## Documentation

- [Getting started](docs/getting-started.md)
- [Generic actions and querying examples](docs/actions.md)
- [Configuration and authentication](docs/configuration.md)
- [Error handling](docs/errors.md)
- [Public API reference](docs/api.md)
- [Development tools and benchmarks](docs/development.md)
- [Architecture](docs/architecture.md)
- [Compatibility and limitations](docs/compatibility.md)
- [Roadmap](docs/roadmap.md)
- [Release process](docs/releasing.md)
- [v0.2.0 release notes](docs/release-notes.md)
- [Changelog](CHANGELOG.md)

Build the documentation locally with `uv run --group docs mkdocs build --strict`,
or preview with `uv run --group docs mkdocs serve`. No hosted documentation URL
is claimed until deployment is configured.

## Development

```console
uv sync --locked --group docs
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run basedpyright
uv run pytest
uv run --group docs mkdocs build --strict
uv build
uv run python scripts/check_artifacts.py
```

Normal tests use mocked HTTP; live portal tests are opt-in. See
[Contributing](CONTRIBUTING.md) and [Security](SECURITY.md).

Existing CKAN clients such as [ckanapi](https://github.com/ckan/ckanapi) serve the
community already. This project's direction is Chile-first defaults, modern
Python typing, and progressively richer sync/async workflows.

## License

[MIT](LICENSE.md). Portal datasets may have their own licenses; the SDK's license
does not determine permission to use upstream data.
