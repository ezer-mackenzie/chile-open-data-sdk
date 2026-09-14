"""Public response models for CKAN Action API envelopes."""

from pydantic import BaseModel, ConfigDict, JsonValue, StrictBool

__all__ = ["ActionResponse"]


class ActionResponse(BaseModel):
    """CKAN envelope with strict success typing and preserved extension metadata.

    This model validates structure only. Use parse_response to enforce result
    presence, map failures, and redact diagnostics; model contents remain raw."""

    model_config = ConfigDict(extra="allow")
    success: StrictBool
    result: JsonValue = None
    error: dict[str, JsonValue] | None = None
