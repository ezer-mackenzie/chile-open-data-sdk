"""Unofficial Chile-first CKAN Action API SDK."""

from chile_open_data.client import ChileOpenDataClient, CKANClient
from chile_open_data.config import ClientConfig
from chile_open_data.types import JSONValue

__version__ = "0.1.0"
__all__ = ["CKANClient", "ChileOpenDataClient", "ClientConfig", "JSONValue", "__version__"]
