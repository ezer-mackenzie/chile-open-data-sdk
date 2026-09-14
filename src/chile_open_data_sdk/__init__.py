"""Unofficial Chile-first CKAN Action API SDK."""

from chile_open_data_sdk import constants
from chile_open_data_sdk.catalog import (
    DatasetService,
    GroupService,
    OrganizationService,
    ResourceService,
    TagService,
)
from chile_open_data_sdk.client import ActionService, ChileOpenDataClient, CKANClient
from chile_open_data_sdk.config import ClientConfig
from chile_open_data_sdk.errors import (
    ChileOpenDataError,
    CKANAPIError,
    CKANAuthenticationError,
    CKANAuthorizationError,
    CKANConnectionError,
    CKANError,
    CKANHTTPError,
    CKANNotFoundError,
    CKANProtocolError,
    CKANRateLimitError,
    CKANTimeoutError,
    CKANValidationError,
)
from chile_open_data_sdk.models import (
    ActionResponse,
    CatalogModel,
    Dataset,
    DatasetSearchResult,
    Group,
    Organization,
    Resource,
    Tag,
)
from chile_open_data_sdk.responses import parse_response, parse_result, redact
from chile_open_data_sdk.types import JSONObject, JSONValue
from chile_open_data_sdk.validation import (
    is_connection_limit,
    validate_identifier,
    validate_page_value,
    validate_tls_verification,
)

__version__ = constants.SDK_VERSION

__all__ = [
    "ActionResponse",
    "ActionService",
    "CKANAPIError",
    "CKANAuthenticationError",
    "CKANAuthorizationError",
    "CKANClient",
    "CKANConnectionError",
    "CKANError",
    "CKANHTTPError",
    "CKANNotFoundError",
    "CKANProtocolError",
    "CKANRateLimitError",
    "CKANTimeoutError",
    "CKANValidationError",
    "CatalogModel",
    "ChileOpenDataClient",
    "ChileOpenDataError",
    "ClientConfig",
    "Dataset",
    "DatasetSearchResult",
    "DatasetService",
    "Group",
    "GroupService",
    "JSONObject",
    "JSONValue",
    "Organization",
    "OrganizationService",
    "Resource",
    "ResourceService",
    "Tag",
    "TagService",
    "__version__",
    "constants",
    "is_connection_limit",
    "parse_response",
    "parse_result",
    "redact",
    "validate_identifier",
    "validate_page_value",
    "validate_tls_verification",
]
