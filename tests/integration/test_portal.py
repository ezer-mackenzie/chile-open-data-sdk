"""Optional live contract: explicitly enabled, public read-only requests only."""

import os

import pytest

from chile_open_data_sdk import ChileOpenDataClient


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("CHILE_OPEN_DATA_LIVE_TESTS") != "1", reason="Live tests are opt-in"
)
def test_portal_package_search():
    with ChileOpenDataClient() as client:
        result = client.actions.call("package_search", {"rows": 1})
    assert isinstance(result, dict)
    assert isinstance(result["count"], int)
    assert isinstance(result["results"], list)


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("CHILE_OPEN_DATA_LIVE_TESTS") != "1", reason="Live tests are opt-in"
)
def test_portal_typed_catalog():
    with ChileOpenDataClient() as client:
        page = client.datasets.search(rows=1)
        assert page.count >= 0
        if page.results:
            details = client.datasets.get(page.results[0].id)
            assert details.id == page.results[0].id
            if details.resources:
                resource = client.resources.get(details.resources[0].id)
                assert resource.id == details.resources[0].id
        client.organizations.list(limit=1)
        client.groups.list(limit=1)
        client.tags.list(query="transport")
