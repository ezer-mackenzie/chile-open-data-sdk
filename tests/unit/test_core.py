"""Contract tests for the synchronous foundation using deterministic HTTPX responses."""

import json
import traceback

import httpx
import pytest

from chile_open_data_sdk import ChileOpenDataClient, CKANClient, ClientConfig
from chile_open_data_sdk.errors import (
    CKANAPIError,
    CKANAuthenticationError,
    CKANAuthorizationError,
    CKANConnectionError,
    CKANError,
    CKANHTTPError,
    CKANNotFoundError,
    CKANProtocolError,
    CKANRateLimitError,
    CKANTimeoutError,
    CKANValidationError,
)


def client_for(response, **kwargs):
    return ChileOpenDataClient(transport=httpx.MockTransport(lambda request: response), **kwargs)


@pytest.mark.parametrize("result", [None, False, 0, "", [], {}, [1, {"title": "Chile"}]])
def test_unwrap_all_json_values(result):
    with client_for(
        httpx.Response(
            200, json={"success": True, "result": result, "extension": {"anything": True}}
        )
    ) as client:
        assert client.actions.call("status_show") == result
    assert client.is_closed


def test_json_post_endpoint_authentication_and_reuse():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"success": True, "result": {"count": 0}})

    config = ClientConfig(
        site_url="https://example.test/ckan/", api_token="test-secret", action_path="/api/3/action/"
    )
    with CKANClient(config=config, transport=httpx.MockTransport(handler)) as client:
        for _ in range(2):
            assert client.actions.call(
                "package_search", {"q": "transport", "rows": 1, "filters": {"region": [1, 2]}}
            ) == {"count": 0}
        assert not client.is_closed
        assert client.config is config
    assert len(requests) == 2
    for request in requests:
        assert str(request.url) == "https://example.test/ckan/api/3/action/package_search"
        assert request.method == "POST"
        assert request.headers["Authorization"] == "test-secret"
        assert request.headers["user-agent"] == "chile-open-data-sdk/0.1.0"
        assert json.loads(request.content)["filters"] == {"region": [1, 2]}
        assert request.extensions["timeout"] == {"connect": 5, "read": 30, "write": 30, "pool": 5}
    assert "test-secret" not in repr(config)
    assert "test-secret" not in repr(client)


def test_default_does_not_read_credentials(monkeypatch):
    monkeypatch.setenv("CHILE_OPEN_DATA_API_TOKEN", "ignored-secret")

    def handler(request):
        assert "Authorization" not in request.headers
        assert str(request.url) == "https://datos.gob.cl/api/3/action/status_show"
        assert json.loads(request.content) == {}
        return httpx.Response(200, json={"success": True, "result": True})

    with ChileOpenDataClient(transport=httpx.MockTransport(handler)) as client:
        assert client.actions.call("status_show") is True


@pytest.mark.parametrize(
    "status,expected",
    [
        (301, CKANHTTPError),
        (400, CKANValidationError),
        (401, CKANAuthenticationError),
        (403, CKANAuthorizationError),
        (404, CKANNotFoundError),
        (409, CKANValidationError),
        (422, CKANValidationError),
        (429, CKANRateLimitError),
        (500, CKANHTTPError),
        (503, CKANHTTPError),
    ],
)
def test_http_errors_and_no_retry(status, expected):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status,
            text="not JSON test-secret",
            headers={"Location": "https://external.test", "Retry-After": "0"},
        )

    with ChileOpenDataClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(expected) as error:
            client.actions.call("datastore_upsert", {"records": []})
    assert len(requests) == 1
    assert error.value.status_code == status
    assert error.value.action == "datastore_upsert"
    assert error.value.details is None
    assert "test-secret" not in str(error.value)


@pytest.mark.parametrize(
    "error_type,expected",
    [
        ("Authorization Error", CKANAuthorizationError),
        ("Authentication Error", CKANAuthenticationError),
        ("Not Found Error", CKANNotFoundError),
        ("Validation Error", CKANValidationError),
        ("Plugin Error", CKANAPIError),
    ],
)
def test_ckan_errors_at_http_200(error_type, expected):
    payload = {"success": False, "error": {"__type": error_type, "message": "denied"}}
    with client_for(httpx.Response(200, json=payload)) as client:
        with pytest.raises(expected) as error:
            client.actions.call("package_show")
    assert error.value.error_type == error_type
    assert error.value.details["message"] == "denied"


def test_http_error_takes_precedence_over_success_envelope():
    with client_for(httpx.Response(403, json={"success": True, "result": 1})) as client:
        with pytest.raises(CKANAuthorizationError):
            client.actions.call("status_show")


@pytest.mark.parametrize(
    "payload",
    [
        "<html>error</html>",
        "[]",
        "null",
        "{}",
        '{"success": "true", "result": 1}',
        '{"success": true}',
        '{"success": true, "result": NaN}',
        '{"success": true, "result": Infinity}',
        '{"success": true, "result": 1, "error": []}',
        "{",
    ],
)
def test_malformed_protocol(payload):
    with client_for(httpx.Response(200, text=payload)) as client:
        with pytest.raises(CKANProtocolError):
            client.actions.call("status_show")


def test_empty_ckan_failure():
    with client_for(httpx.Response(200, json={"success": False})) as client:
        with pytest.raises(CKANAPIError):
            client.actions.call("status_show")


def test_recursive_secret_redaction():
    token = "test-secret"
    payload = {
        "success": False,
        "error": {
            "__type": "Plugin " + token,
            "message": "echo " + token,
            "api_token": "another secret",
            "Authorization": "other",
            "nested": [{token: token, "password": "different", "value": 42, "ok": None}],
        },
    }
    with client_for(httpx.Response(200, json=payload), api_token=token) as client:
        with pytest.raises(CKANAPIError) as error:
            client.actions.call("status_show")
    diagnostic = repr(vars(error.value)) + repr(error.value) + str(error.value)
    for secret in [token, "another secret", "other", "different"]:
        assert secret not in diagnostic
    assert error.value.details["nested"][0]["value"] == 42


@pytest.mark.parametrize(
    "exception,expected",
    [
        (httpx.ConnectTimeout, CKANTimeoutError),
        (httpx.ReadTimeout, CKANTimeoutError),
        (httpx.WriteTimeout, CKANTimeoutError),
        (httpx.PoolTimeout, CKANTimeoutError),
        (httpx.ConnectError, CKANConnectionError),
        (httpx.RemoteProtocolError, CKANConnectionError),
    ],
)
def test_transport_errors_do_not_leak_secrets_or_retry(exception, expected):
    calls = []

    def handler(request):
        calls.append(request)
        raise exception("test-secret", request=request)

    with ChileOpenDataClient(
        api_token="test-secret", transport=httpx.MockTransport(handler)
    ) as client:
        with pytest.raises(expected) as error:
            client.actions.call("package_list")
    assert len(calls) == 1
    assert "test-secret" not in "".join(traceback.format_exception(error.value))
    assert error.value.__context__ is None


@pytest.mark.parametrize(
    "action", ["../status_show", "https://external.test", "a/b", "x?q=1", "", "a#b"]
)
def test_invalid_action_never_reaches_transport(action):
    def handler(request):
        pytest.fail("Invalid action reached transport")

    with ChileOpenDataClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError):
            client.actions.call(action)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), object()])
def test_invalid_json_parameters(value):
    with client_for(httpx.Response(200)) as client:
        with pytest.raises(ValueError, match="JSON-compatible"):
            client.actions.call("status_show", {"value": value})


def test_lifecycle_closes_on_exception_and_cannot_reopen():
    client = client_for(httpx.Response(200))
    with pytest.raises(RuntimeError), client:
        raise RuntimeError("application failure")
    client.close()
    assert client.is_closed
    with pytest.raises(CKANError, match="closed"):
        client.actions.call("status_show")
    with pytest.raises(CKANError, match="closed"), client:
        pass


def test_constructor_conflicts():
    with pytest.raises(ValueError):
        CKANClient()
    with pytest.raises(ValueError):
        CKANClient("https://example.test", config=ClientConfig())
    with pytest.raises(ValueError):
        ChileOpenDataClient(api_token="test-token", config=ClientConfig())
    with ChileOpenDataClient(config=ClientConfig()) as client:
        assert client.config.site_url == "https://datos.gob.cl"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.test",
        "",
        "https://user:pass@example.test",
        "https://example.test?token=secret",
        "https://example.test/#fragment",
        "https://[broken",
        "https://example.test:bad",
        "https://example.test:0",
        "https://exa mple.test",
        "https://example.test/../bad",
        "https://example.test/%2e%2e",
        "https://example.test\\bad",
    ],
)
def test_invalid_site_urls(url):
    with pytest.raises(ValueError) as error:
        ClientConfig(site_url=url)
    assert "secret" not in str(error.value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"action_path": "//evil.test"},
        {"action_path": "/../action"},
        {"connect_timeout": 0},
        {"read_timeout": -1},
        {"write_timeout": float("inf")},
        {"pool_timeout": float("nan")},
        {"read_timeout": True},
        {"max_connections": 0},
        {"max_connections": 1.5},
        {"max_keepalive_connections": -1},
        {"max_connections": 1, "max_keepalive_connections": 2},
        {"api_token": "secret\r\nheader"},
        {"api_token": ""},
        {"user_agent": ""},
        {"verify": "false"},
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        ClientConfig(**kwargs)


def test_configuration_is_frozen():
    from dataclasses import FrozenInstanceError

    config = ClientConfig()
    with pytest.raises(FrozenInstanceError):
        config.site_url = "https://external.test"


def test_chile_client_rejects_empty_explicit_url():
    with pytest.raises(ValueError):
        ChileOpenDataClient(site_url="")
