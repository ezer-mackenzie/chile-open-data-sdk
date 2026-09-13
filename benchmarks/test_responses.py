"""Opt-in CPU benchmarks; no network calls or timing assertions."""

import httpx
from pytest_benchmark.fixture import BenchmarkFixture

from chile_open_data._internal.responses import parse_response, redact
from chile_open_data.types import JSONValue


def test_parse_datastore_page(benchmark: BenchmarkFixture) -> None:
    records = [{"_id": i, "region": "Metropolitana", "value": i / 10} for i in range(1000)]
    response = httpx.Response(200, json={"success": True, "result": {"records": records}})
    result = benchmark(parse_response, response, "datastore_search", None)
    assert result == {"records": records}


def test_redact_nested_diagnostics(benchmark: BenchmarkFixture) -> None:
    token = "sdk_secret_benchmark_fixture"
    payload: JSONValue = {
        "errors": [{"message": "echo " + token, "api_token": token} for _ in range(100)]
    }
    result = benchmark(redact, payload, token)
    assert token not in repr(result)
