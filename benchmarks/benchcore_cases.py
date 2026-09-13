"""Explicitly selected BenchCore measurements; excluded from normal test discovery."""

import httpx
import pytest
from benchcore.core.models import BenchmarkConfig
from benchcore.integrations.pytest import BenchCoreFixture

from chile_open_data_sdk._internal.responses import parse_response, redact
from chile_open_data_sdk.types import JSONValue


@pytest.mark.benchcore(
    name="parse-datastore-page[rows=1000]",
    config=BenchmarkConfig(rounds=20, warmup_rounds=2, iterations=10),
)
def test_parse_datastore_page(benchcore: BenchCoreFixture) -> None:
    records = [{"_id": i, "region": "Metropolitana", "value": i / 10} for i in range(1000)]
    response = httpx.Response(200, json={"success": True, "result": {"records": records}})
    result = benchcore(parse_response, response, "datastore_search", None)
    assert result.value == {"records": records}


@pytest.mark.benchcore(
    name="redact-diagnostics[entries=100]",
    config=BenchmarkConfig(rounds=20, warmup_rounds=2, iterations=10),
)
def test_redact_nested_diagnostics(benchcore: BenchCoreFixture) -> None:
    token = "sdk_secret_benchcore_fixture"
    payload: JSONValue = {
        "errors": [{"message": "echo " + token, "api_token": token} for _ in range(100)]
    }
    result = benchcore(redact, payload, token)
    assert token not in repr(result.value)
