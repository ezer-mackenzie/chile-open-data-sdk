"""Shared JSON types for schema-independent CKAN action data."""

from typing import TypeAlias, TypeVar

JSONValue: TypeAlias = bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"] | None

JSONObject: TypeAlias = dict[str, JSONValue]
"""A JSON object with string keys and recursively typed values."""


ResultT = TypeVar("ResultT")
