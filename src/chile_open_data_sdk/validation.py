"""Runtime validators for untrusted connection settings."""

from typing import TypeGuard

__all__ = ["is_connection_limit", "validate_tls_verification"]


def is_connection_limit(value: object) -> TypeGuard[int]:
    """Narrow untrusted runtime input to an integer, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def validate_tls_verification(value: object) -> None:
    """Reject untyped inputs that could accidentally disable TLS verification."""
    if not isinstance(value, bool):
        raise ValueError("verify must be a boolean")
