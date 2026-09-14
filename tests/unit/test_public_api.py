"""Contracts for directly reusable public SDK components."""

import httpx
import pytest
from pydantic import ValidationError

from chile_open_data_sdk import (
    ActionResponse,
    CKANAuthenticationError,
    CKANProtocolError,
    JSONObject,
    constants,
    parse_response,
    redact,
)


def test_direct_parser_redacts_diagnostic_action_and_details() -> None:
    response = httpx.Response(
        401, json={"success": False, "error": {"message": "credential-example"}}
    )
    with pytest.raises(CKANAuthenticationError) as caught:
        parse_response(response, "credential-example", token="credential-example")
    assert caught.value.action == "[REDACTED]"
    assert caught.value.details == {"message": "[REDACTED]"}


def test_direct_helpers_without_configured_token() -> None:
    payload: JSONObject = {"success": True, "result": {"count": 3}}
    assert parse_response(httpx.Response(200, json=payload), "package_search") == {"count": 3}
    source: JSONObject = {"api_key": "example", "nested": [1, None]}
    assert redact(source) == {"api_key": "[REDACTED]", "nested": [1, None]}
    assert source["api_key"] == "example"


def test_model_preserves_extensions_but_parser_requires_result() -> None:
    model = ActionResponse.model_validate({"success": True, "extension": {"count": 2}})
    assert model.model_extra == {"extension": {"count": 2}}
    with pytest.raises(CKANProtocolError):
        parse_response(httpx.Response(200, json=model.model_dump(exclude_unset=True)), "test")
    with pytest.raises(ValidationError):
        ActionResponse.model_validate({"success": "true", "result": None})


def test_error_mappings_cannot_be_modified() -> None:
    with pytest.raises(TypeError):
        constants.HTTP_ERROR_TYPES[401] = CKANProtocolError  # type: ignore[index]
    assert constants.HTTP_ERROR_TYPES[401] is CKANAuthenticationError
