# Catalog discovery

v0.2.0 adds typed, synchronous metadata access on both `CKANClient` and
`ChileOpenDataClient`. Every non-iterator call makes one Action API request.
These services read metadata; they do not download resources or write datasets.

## Find datasets and resources

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    names = client.datasets.list(limit=10, offset=0)
    page = client.datasets.search("transport", fq="res_format:CSV", rows=5)
    print(page.count)
    for dataset in page.results:
        print(dataset.id, dataset.title)
        details = client.datasets.get(dataset.id)
        for resource in details.resources:
            metadata = client.resources.get(resource.id)
            print(metadata.url, metadata.format)
```

| Method | CKAN action | Result |
| --- | --- | --- |
| `datasets.list(limit=100, offset=0)` | `package_list` | `list[str]` of names |
| `datasets.get(id)` | `package_show` | `Dataset` |
| `datasets.search(q="*:*", ...)` | `package_search` | `DatasetSearchResult` |
| `resources.get(id)` | `resource_show` | `Resource` |
| `organizations.list(limit=25, offset=0, sort="name asc")` | `organization_list` | `list[Organization]` |
| `organizations.get(id)` | `organization_show` | `Organization` |
| `groups.list(limit=25, offset=0, sort="name asc")` | `group_list` | `list[Group]` |
| `groups.get(id)` | `group_show` | `Group` |
| `tags.list(query=None, vocabulary_id=None)` | `tag_list` | `list[Tag]` |
| `tags.get(id, vocabulary_id=None)` | `tag_show` | `Tag` |

Dataset, organization, group, and tag lookups accept IDs or names. Resource
lookups require a resource ID. IDs remain strings. List limits must be positive
integers; offsets must be nonnegative integers. Booleans are not page integers.
Organizations and groups request `all_fields=True`. Their detail requests exclude
embedded users and datasets; tag details exclude embedded datasets. Tag listing
is one unpaginated upstream request; use query/vocabulary filters where possible.

## Search parameters and extensions

`q`, `fq`, and `sort` are passed through unchanged. `search` defaults to `rows=10`,
`start=0`, and the server's sort order. `rows=0` requests counts/facets without
result rows. Search results expose `count`, `results`, `facets`, and `search_facets`.

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    counts = client.datasets.search(
        rows=0,
        extra_params={"facet.field": ["tags"], "facet.limit": 10},
    )
    print(counts.search_facets)
```

`extra_params` accepts JSON-compatible plugin or dotted facet parameters. It
cannot override `q`, `fq`, `sort`, `rows`, or `start`; conflicts raise ValueError
before HTTP. Unsupported parameters and permissions are handled by the server.
For actions or schemas outside these models, use `client.actions.call`.

## Explicit lazy pagination

```python
from chile_open_data_sdk import ChileOpenDataClient

with ChileOpenDataClient() as client:
    for dataset in client.datasets.iter_search("transport", page_size=50, max_items=120):
        print(dataset.title)
```

`iter_search` yields `Dataset` objects; `iter_pages` yields complete
`DatasetSearchResult` pages, including facets. Both accept `q`, `fq`, `sort`,
`page_size`, `start`, and `extra_params`. `iter_search` additionally accepts
`max_items`: None deliberately iterates the matching catalog, and zero makes no
request. Generator validation happens when iteration begins.

Pages are fetched only when consumed, with no prefetch. Iteration defaults to
`sort="id asc"` and `page_size=100`. A custom sort should include a unique
identifier as a tie-breaker. Offsets advance by the number actually returned,
so a server-imposed smaller page size does not skip records. Iteration stops on
an empty page or when the offset reaches the first page's count. A consecutive
repeated page raises `CKANProtocolError` instead of silently repeating data.

Only one page and its previous ID signature are retained. `max_items` limits
yielded items, not the server's final page size. Stop consuming to stop requests,
and keep the client open during iteration. Offset pagination is not a snapshot:
concurrent inserts, removals, or reordering can still cause missing or duplicate
items. The initial count bounds the traversal even if the catalog grows.

## Metadata and errors

Models require identity fields but accept omitted or nullable optional metadata.
Nested dataset resources, organizations, groups, and tags are typed. Plugin fields
survive validation and `model_dump(exclude_unset=True)`; inspect `model_extra` for
extensions. Dates and resource URLs remain strings, including historical formats
and relative paths. Resource metadata access never fetches those URLs.

Malformed typed results raise `CKANProtocolError` with a fixed action label and
no raw Pydantic input details or exception chain. Other HTTP, CKAN, timeout, and
connection errors retain the generic client's behavior. Direct model construction
uses normal Pydantic validation and its errors may contain input data.

The mappings follow the [CKAN Action API reference](https://docs.ckan.org/en/2.11/api/).
Portal plugins, limits, and metadata completeness can differ; this SDK does not
infer a server's CKAN version or guarantee catalog consistency across requests.
