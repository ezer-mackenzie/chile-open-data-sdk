"""Offline catalog contracts, including schema tolerance and pagination behavior."""

import json
import traceback

import httpx
import pytest
from pydantic import ValidationError

from chile_open_data_sdk import (
    CKANClient,
    CKANError,
    CKANNotFoundError,
    CKANProtocolError,
    Dataset,
    DatasetSearchResult,
    Group,
    Organization,
    Resource,
    Tag,
)


def dataset(index=0):
    return {
        "id": f"dataset-{index}",
        "name": f"dataset-{index}",
        "title": "Transport",
        "metadata_modified": "legacy date",
        "plugin": {"region": ["Chile"]},
        "resources": [
            {
                "id": "resource-1",
                "url": "relative/path",
                "format": "CSV",
                "size": "unknown",
                "last_modified": "",
                "plugin": {"a": True},
            }
        ],
        "organization": {"id": "org-1", "name": "ministry", "title": None},
        "groups": [{"id": "group-1", "name": "transport"}],
        "tags": [{"id": "tag-1", "name": "mobility", "vocabulary_id": None}],
    }


def make_client(result, requests=None):
    def handler(request):
        if requests is not None:
            requests.append(request)
        return httpx.Response(200, json={"success": True, "result": result})

    return CKANClient("https://catalog.test/prefix", transport=httpx.MockTransport(handler))


def test_metadata_preserves_extensions_and_conservative_strings():
    raw = dataset()
    parsed = Dataset.model_validate(raw)
    assert isinstance(parsed.resources[0], Resource)
    assert isinstance(parsed.organization, Organization)
    assert isinstance(parsed.groups[0], Group)
    assert isinstance(parsed.tags[0], Tag)
    assert parsed.metadata_modified == "legacy date"
    assert parsed.resources[0].url == "relative/path"
    assert parsed.resources[0].size == "unknown"
    assert parsed.model_dump(exclude_unset=True) == raw
    first = Dataset(id="one", name="one")
    second = Dataset(id="two", name="two")
    first.resources.append(Resource(id="r"))
    assert second.resources == []
    assert Dataset.model_validate({"id": "a", "name": "a", "private": "false"}).private is False


@pytest.mark.parametrize(
    "service,action,raw,model",
    [
        ("datasets", "package_show", dataset(), Dataset),
        ("resources", "resource_show", {"id": "r", "name": None}, Resource),
        ("organizations", "organization_show", {"id": "o", "name": "o"}, Organization),
        ("groups", "group_show", {"id": "g", "name": "g"}, Group),
        ("tags", "tag_show", {"id": "t", "name": "t"}, Tag),
    ],
)
def test_get_metadata_routes_through_shared_actions(service, action, raw, model):
    requests = []
    with make_client(raw, requests) as client:
        accessor = getattr(client, service)
        assert accessor.actions is client.actions
        assert isinstance(accessor.get("alias with spaces"), model)
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == f"https://catalog.test/prefix/api/3/action/{action}"
    params = json.loads(request.content)
    assert params["id"] == "alias with spaces"
    if service in {"organizations", "groups", "tags"}:
        assert params["include_datasets"] is False
    if service in {"organizations", "groups"}:
        assert params["include_users"] is False


@pytest.mark.parametrize(
    "service,action,raw",
    [
        ("datasets", "package_list", ["one", "two"]),
        ("organizations", "organization_list", [{"id": "o", "name": "o"}]),
        ("groups", "group_list", [{"id": "g", "name": "g"}]),
    ],
)
def test_lists_are_single_pages(service, action, raw):
    requests = []
    with make_client(raw, requests) as client:
        result = getattr(client, service).list(limit=2, offset=3)
        assert len(result) == len(raw)
    assert len(requests) == 1
    assert requests[0].url.path.endswith(action)
    params = json.loads(requests[0].content)
    assert params["limit"] == 2 and params["offset"] == 3
    if service != "datasets":
        assert params["all_fields"] is True
        assert params["sort"] == "name asc"


def test_tags_query_and_vocabulary():
    requests = []
    with make_client([{"id": "tag", "name": "mobility"}], requests) as client:
        assert client.tags.list(query="mob", vocabulary_id="v")[0].name == "mobility"
        client.tags.list()
    assert json.loads(requests[0].content) == {
        "query": "mob",
        "vocabulary_id": "v",
        "all_fields": True,
    }
    assert json.loads(requests[1].content) == {"all_fields": True}
    with make_client({"id": "tag", "name": "mobility"}, requests) as client:
        client.tags.get("mobility", vocabulary_id="v")
    assert json.loads(requests[-1].content)["vocabulary_id"] == "v"


def test_search_forwards_query_and_facets_without_mutation():
    requests = []
    facets = {"tags": {"title": "Tags", "items": [{"name": "rail", "count": 2}]}}
    extras = {"facet.field": ["tags"], "facet.limit": 5, "include_private": False}
    with make_client(
        {"count": 2, "results": [dataset()], "search_facets": facets, "plugin": {"a": 3}}, requests
    ) as client:
        result = client.datasets.search(
            "rail OR bus",
            fq="res_format:CSV",
            sort="name asc",
            rows=2,
            start=4,
            extra_params=extras,
        )
    assert isinstance(result, DatasetSearchResult)
    assert result.search_facets == facets
    assert result.model_extra == {"plugin": {"a": 3}}
    assert json.loads(requests[0].content) == {
        "q": "rail OR bus",
        "fq": "res_format:CSV",
        "sort": "name asc",
        "rows": 2,
        "start": 4,
        **extras,
    }
    assert extras == {"facet.field": ["tags"], "facet.limit": 5, "include_private": False}


def test_count_only_and_search_defaults():
    requests = []
    with make_client({"count": 42, "results": []}, requests) as client:
        assert client.datasets.search(rows=0).count == 42
    assert json.loads(requests[0].content) == {"q": "*:*", "rows": 0, "start": 0}


@pytest.mark.parametrize("service", ["datasets", "resources", "organizations", "groups", "tags"])
@pytest.mark.parametrize("identifier", ["", "  ", None, 1])
def test_invalid_identifiers_fail_before_http(service, identifier):
    requests = []
    with make_client(None, requests) as client, pytest.raises(ValueError, match="nonempty"):
        getattr(client, service).get(identifier)
    assert requests == []


@pytest.mark.parametrize("bad", [-1, True, 1.5, "2"])
def test_invalid_pagination_parameters_fail_before_http(bad):
    requests = []
    with make_client(None, requests) as client:
        for service in (client.datasets, client.organizations, client.groups):
            with pytest.raises(ValueError):
                service.list(limit=bad)
            with pytest.raises(ValueError):
                service.list(offset=bad)
        with pytest.raises(ValueError):
            client.datasets.search(rows=bad)
        with pytest.raises(ValueError):
            client.datasets.search(start=bad)
        with pytest.raises(ValueError):
            list(client.datasets.iter_search(max_items=bad))
        with pytest.raises(ValueError):
            list(client.datasets.iter_pages(page_size=bad))
    assert requests == []


def test_zero_page_sizes_and_conflicting_extra_params():
    requests = []
    with make_client(None, requests) as client:
        with pytest.raises(ValueError):
            client.datasets.list(limit=0)
        with pytest.raises(ValueError):
            list(client.datasets.iter_search(page_size=0))
        for key in ("q", "fq", "sort", "start", "rows"):
            with pytest.raises(ValueError, match="override"):
                client.datasets.search(extra_params={key: 2})
    assert requests == []


@pytest.mark.parametrize(
    "raw",
    [
        None,
        [],
        {},
        {"count": -1, "results": []},
        {"count": True, "results": []},
        {"count": "1", "results": []},
        {"count": 1, "results": [{"id": "secret-value"}]},
    ],
)
def test_bad_typed_results_raise_safe_protocol_errors(raw):
    with make_client(raw) as client, pytest.raises(CKANProtocolError) as caught:
        client.datasets.search()
    assert caught.value.action == "package_search"
    assert caught.value.details is None
    assert caught.value.__context__ is None
    assert "secret-value" not in "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("service", ["datasets", "organizations", "groups", "tags"])
def test_malformed_lists_raise_protocol_errors(service):
    with make_client([123]) as client, pytest.raises(CKANProtocolError):
        getattr(client, service).list()


def test_http_errors_and_lifecycle_are_shared():
    def handler(request):
        return httpx.Response(404, json={"success": False, "error": {"message": "gone"}})

    with CKANClient("https://catalog.test", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(CKANNotFoundError):
            client.datasets.get("missing")
    with pytest.raises(CKANError, match="closed"):
        client.resources.get("resource")


def paging_client(responses, requests):
    pages = iter(responses)

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"success": True, "result": next(pages)})

    return CKANClient("https://catalog.test", transport=httpx.MockTransport(handler))


def test_iteration_is_lazy_and_handles_server_page_caps():
    requests = []
    pages = [{"count": 5, "results": [dataset(i)]} for i in range(2, 5)]
    with paging_client(pages, requests) as client:
        iterator = client.datasets.iter_search("rail", fq="format:CSV", page_size=100, start=2)
        assert requests == []
        assert [item.id for item in iterator] == ["dataset-2", "dataset-3", "dataset-4"]
    assert [r["start"] for r in requests] == [2, 3, 4]
    assert all(r["sort"] == "id asc" and r["q"] == "rail" and r["rows"] == 100 for r in requests)


def test_max_items_stops_without_another_request():
    requests = []
    with paging_client(
        [{"count": 10, "results": [dataset(i) for i in range(3)]}], requests
    ) as client:
        assert list(client.datasets.iter_search(max_items=0)) == []
        assert requests == []
        assert len(list(client.datasets.iter_search(max_items=2))) == 2
    assert len(requests) == 1


def test_consumer_can_stop_iteration_without_prefetch():
    requests = []
    with paging_client([{"count": 10, "results": [dataset()]}], requests) as client:
        iterator = client.datasets.iter_search()
        assert next(iterator).id == "dataset-0"
        iterator.close()
    assert len(requests) == 1


@pytest.mark.parametrize("count", [0, 100])
def test_empty_page_stops_even_with_stale_count(count):
    requests = []
    with paging_client([{"count": count, "results": []}], requests) as client:
        assert list(client.datasets.iter_pages()) == []
    assert len(requests) == 1


def test_pagination_stops_at_initial_count_when_catalog_grows():
    requests = []
    pages = [{"count": 2, "results": [dataset(0)]}, {"count": 100, "results": [dataset(1)]}]
    with paging_client(pages, requests) as client:
        assert len(list(client.datasets.iter_search())) == 2
    assert len(requests) == 2


def test_repeated_page_is_a_protocol_error():
    requests = []
    page = {"count": 5, "results": [dataset()]}
    with (
        paging_client([page, page], requests) as client,
        pytest.raises(CKANProtocolError, match="advance"),
    ):
        list(client.datasets.iter_search())
    assert len(requests) == 2


def test_direct_model_reports_validation_errors():
    with pytest.raises(ValidationError):
        Dataset.model_validate({"name": "missing-id"})
