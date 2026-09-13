"""Generated JSON contracts and credential-redaction invariants."""

import copy
import json

import httpx
from hypothesis import given
from hypothesis import strategies as st

from chile_open_data._internal.responses import parse_response, redact
from chile_open_data.types import JSONValue

json_values = st.recursive(
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats(allow_nan=False, allow_infinity=False)
    | st.text(),
    lambda children: (
        st.lists(children, max_size=5) | st.dictionaries(st.text(), children, max_size=5)
    ),
    max_leaves=20,
)


@given(json_values)
def test_json_results_preserve_structure(value: JSONValue) -> None:
    response = httpx.Response(200, json={"success": True, "result": value})
    assert parse_response(response, "status_show", None) == value


@given(json_values)
def test_redaction_preserves_input_and_removes_nested_token(value: JSONValue) -> None:
    token = "sdk_secret_property_fixture"
    payload: JSONValue = {
        "data": value,
        "nested": [{"message": "echo " + token, token: token}],
        "Authorization": "separate-credential",
    }
    original = copy.deepcopy(payload)
    sanitized = redact(payload, token)
    assert token not in json.dumps(sanitized)
    assert "separate-credential" not in json.dumps(sanitized)
    assert payload == original
    assert redact(sanitized, token) == sanitized
