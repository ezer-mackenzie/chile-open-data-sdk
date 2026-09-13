"""Unofficial Chile-first CKAN Action API SDK."""

from chile_open_data_sdk.client import ChileOpenDataClient, CKANClient
from chile_open_data_sdk.config import ClientConfig
from chile_open_data_sdk.types import JSONValue

__version__ = "0.1.0"
__all__ = ["CKANClient", "ChileOpenDataClient", "ClientConfig", "JSONValue", "__version__"]
