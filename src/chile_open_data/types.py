"""Shared JSON types for schema-independent CKAN action data."""

from typing import TypeAlias

JSONValue: TypeAlias = bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"] | None
