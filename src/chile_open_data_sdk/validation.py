"""Runtime validators for untrusted connection settings."""

from typing import TypeGuard


def is_connection_limit(value: object) -> TypeGuard[int]:
    """Narrow untrusted runtime input to an integer, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def validate_tls_verification(value: object) -> None:
    """Reject untyped inputs that could accidentally disable TLS verification."""
    if not isinstance(value, bool):
        raise ValueError("verify must be a boolean")


def validate_page_value(value: object, name: str, *, minimum: int = 0) -> None:
    """Require an integer page parameter at or above minimum; exclude booleans.

    Use a fixed parameter name, not untrusted data, for the diagnostic label.
    """
    if not is_connection_limit(value) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def validate_identifier(value: object) -> None:
    """Require a nonempty string identifier without rewriting names or aliases."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("id must be a nonempty string")
