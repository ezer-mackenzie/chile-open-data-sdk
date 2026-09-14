"""Parse CKAN envelopes and redact diagnostic payloads."""

import json
from typing import cast

import httpx
from pydantic import TypeAdapter, ValidationError

from chile_open_data_sdk.constants import (
    CKAN_ERROR_TYPES,
    CREDENTIAL_KEY_PARTS,
    HTTP_ERROR_TYPES,
    REDACTED_VALUE,
)
from chile_open_data_sdk.errors import (
    CKANAPIError,
    CKANHTTPError,
    CKANProtocolError,
)
from chile_open_data_sdk.models import ActionResponse
from chile_open_data_sdk.types import JSONValue, ResultT


def redact(value: JSONValue, token: str | None = None) -> JSONValue:
    """Remove configured tokens and values of credential-like diagnostic keys."""
    if isinstance(value, str):
        return value.replace(token, REDACTED_VALUE) if token else value
    if isinstance(value, list):
        return [redact(item, token) for item in value]
    if isinstance(value, dict):
        return {
            str(redact(key, token)): (
                REDACTED_VALUE
                if any(part in key.lower() for part in CREDENTIAL_KEY_PARTS)
                else redact(item, token)
            )
            for key, item in value.items()
        }
    return value


def parse_response(response: httpx.Response, action: str, token: str | None = None) -> JSONValue:
    """Return only the result; convert HTTP, CKAN, and malformed response failures."""
    action = str(redact(action, token))
    envelope = None
    try:
        envelope = ActionResponse.model_validate_json(response.content)
    except (ValidationError, ValueError):
        pass
    status = response.status_code
    if not response.is_success or (envelope is not None and not envelope.success):
        details = redact(cast(JSONValue, envelope.error), token) if envelope else None
        error_type = details.get("__type") if isinstance(details, dict) else None
        error_type = error_type if isinstance(error_type, str) else None
        error_class = HTTP_ERROR_TYPES.get(status)
        if error_class is None:
            error_class = CKAN_ERROR_TYPES.get(error_type or "")
        if error_class is None:
            error_class = CKANHTTPError if not response.is_success else CKANAPIError
        raise error_class(
            "CKAN action failed",
            action=action,
            status_code=status,
            error_type=error_type,
            details=details,
        )
    if envelope is None or "result" not in envelope.model_fields_set:
        raise CKANProtocolError("Invalid CKAN response envelope", action=action, status_code=status)
    # The JSON parser must reject non-standard NaN/Infinity accepted by some decoders.
    result: JSONValue = envelope.result
    try:
        json.dumps(result, allow_nan=False)
    except ValueError:
        raise CKANProtocolError(
            "Non-finite JSON result", action=action, status_code=status
        ) from None
    return result


def parse_result(value: JSONValue, adapter: TypeAdapter[ResultT], action: str) -> ResultT:
    """Validate an unwrapped result without retaining raw Pydantic error inputs.

    The action must be a safe diagnostic label. SDK services supply fixed action
    names. Invalid typed results raise CKANProtocolError with no raw error chain.
    """
    try:
        return adapter.validate_python(value)
    except ValidationError:
        pass
    raise CKANProtocolError("Invalid CKAN action result", action=action)
