"""SDK exceptions with safe action context; raw requests and responses are not retained."""

from chile_open_data.types import JSONValue


class ChileOpenDataError(Exception):
    """Base exception for SDK runtime failures."""


class CKANError(ChileOpenDataError):
    """CKAN failure with sanitized diagnostic context."""

    def __init__(
        self,
        message: str,
        *,
        action: str,
        status_code: int | None = None,
        error_type: str | None = None,
        details: JSONValue = None,
    ) -> None:
        super().__init__(message)
        self.action = action
        self.status_code = status_code
        self.error_type = error_type
        self.details = details


class CKANAPIError(CKANError):
    """CKAN returned success=false."""


class CKANProtocolError(CKANError):
    """The response was not a valid CKAN JSON envelope."""


class CKANHTTPError(CKANError):
    """An HTTP response was unsuccessful, including redirects."""


class CKANAuthenticationError(CKANAPIError, CKANHTTPError):
    """Authentication is required or failed."""


class CKANAuthorizationError(CKANAPIError, CKANHTTPError):
    """The server denied permission."""


class CKANNotFoundError(CKANAPIError, CKANHTTPError):
    """The requested action or entity was not found."""


class CKANValidationError(CKANAPIError, CKANHTTPError):
    """The server rejected the action parameters."""


class CKANRateLimitError(CKANAPIError, CKANHTTPError):
    """The server rate limited the request; it was not retried."""


class CKANTimeoutError(CKANError):
    """A connect, read, write, or pool timeout occurred."""


class CKANConnectionError(CKANError):
    """HTTPX could not complete the request."""
