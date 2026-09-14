"""SDK defaults and read-only response error mappings.

Configure individual clients with ClientConfig; these constants are not mutable
process-wide settings. Timeout values are seconds and patterns use fullmatch.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from chile_open_data_sdk.errors import (
    CKANAuthenticationError,
    CKANAuthorizationError,
    CKANError,
    CKANNotFoundError,
    CKANRateLimitError,
    CKANValidationError,
)

SDK_VERSION: Final = "0.1.0"
DEFAULT_SITE_URL: Final = "https://datos.gob.cl"
DEFAULT_ACTION_PATH: Final = "/api/3/action"
DEFAULT_USER_AGENT: Final = f"chile-open-data-sdk/{SDK_VERSION}"
DEFAULT_CONNECT_TIMEOUT: Final = 5.0
DEFAULT_READ_TIMEOUT: Final = 30.0
DEFAULT_WRITE_TIMEOUT: Final = 30.0
DEFAULT_POOL_TIMEOUT: Final = 5.0
DEFAULT_MAX_CONNECTIONS: Final = 100
DEFAULT_MAX_KEEPALIVE_CONNECTIONS: Final = 20
ACTION_NAME_PATTERN: Final = r"[A-Za-z][A-Za-z0-9_]*"
ACTION_PATH_PATTERN: Final = r"/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+/?"
REDACTED_VALUE: Final = "[REDACTED]"
CREDENTIAL_KEY_PARTS: Final = (
    "token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "apikey",
)

HTTP_ERROR_TYPES: Final[Mapping[int, type[CKANError]]] = MappingProxyType(
    {
        400: CKANValidationError,
        401: CKANAuthenticationError,
        403: CKANAuthorizationError,
        404: CKANNotFoundError,
        409: CKANValidationError,
        422: CKANValidationError,
        429: CKANRateLimitError,
    }
)
CKAN_ERROR_TYPES: Final[Mapping[str, type[CKANError]]] = MappingProxyType(
    {
        "Authentication Error": CKANAuthenticationError,
        "Authorization Error": CKANAuthorizationError,
        "Not Found Error": CKANNotFoundError,
        "Validation Error": CKANValidationError,
    }
)
