"""Optional live contract: explicitly enabled, public read-only requests only."""

import os

import pytest

from chile_open_data import ChileOpenDataClient


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
