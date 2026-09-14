"""Validated, immutable connection settings; constructors never read credentials implicitly."""

import re
from dataclasses import dataclass, field
from math import isfinite
from urllib.parse import urlsplit

from chile_open_data_sdk.constants import (
    ACTION_PATH_PATTERN,
    DEFAULT_ACTION_PATH,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_CONNECTIONS,
    DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
    DEFAULT_POOL_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_SITE_URL,
    DEFAULT_USER_AGENT,
    DEFAULT_WRITE_TIMEOUT,
)
from chile_open_data_sdk.validation import is_connection_limit, validate_tls_verification

__all__ = ["ClientConfig"]


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Configure a CKAN endpoint, timeouts in seconds, and connection pool limits.

    ``site_url`` can include a deployment prefix. TLS verification is enabled and
    redirects are deliberately disabled. ``api_token`` is excluded from repr.
    """

    site_url: str = DEFAULT_SITE_URL
    action_path: str = DEFAULT_ACTION_PATH
    api_token: str | None = field(default=None, repr=False)
    user_agent: str = DEFAULT_USER_AGENT
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    read_timeout: float = DEFAULT_READ_TIMEOUT
    write_timeout: float = DEFAULT_WRITE_TIMEOUT
    pool_timeout: float = DEFAULT_POOL_TIMEOUT
    max_connections: int = DEFAULT_MAX_CONNECTIONS
    max_keepalive_connections: int = DEFAULT_MAX_KEEPALIVE_CONNECTIONS
    verify: bool = True

    def __post_init__(self) -> None:
        """Reject ambiguous endpoints and invalid settings without echoing credentials."""
        try:
            url = urlsplit(self.site_url)
            valid = (
                url.scheme in {"http", "https"}
                and bool(url.hostname)
                and url.username is None
                and url.password is None
                and not url.query
                and not url.fragment
                and url.port != 0
                and not any(c.isspace() or ord(c) < 32 for c in self.site_url)
                and "\\" not in self.site_url
                and all(p not in {".", ".."} for p in url.path.split("/"))
                and "%" not in url.path
            )
        except ValueError:
            valid = False
        if not valid:
            raise ValueError(
                "site_url must be an HTTP(S) URL without credentials, query or fragment"
            )
        if not re.fullmatch(ACTION_PATH_PATTERN, self.action_path):
            raise ValueError("action_path must contain only absolute path segments")
        object.__setattr__(self, "site_url", self.site_url.rstrip("/"))
        object.__setattr__(self, "action_path", self.action_path.rstrip("/"))
        for value in (
            self.connect_timeout,
            self.read_timeout,
            self.write_timeout,
            self.pool_timeout,
        ):
            if isinstance(value, bool) or not isfinite(value) or value <= 0:
                raise ValueError("Timeouts must be finite positive seconds")
        if (
            not is_connection_limit(self.max_connections)
            or self.max_connections < 1
            or not is_connection_limit(self.max_keepalive_connections)
            or not 0 <= self.max_keepalive_connections <= self.max_connections
        ):
            raise ValueError("Connection limits must be integers with 0 <= keepalive <= maximum")
        for header_value in (self.user_agent, self.api_token):
            if header_value is not None and (
                not header_value or any(ord(c) < 32 or ord(c) > 126 for c in header_value)
            ):
                raise ValueError("Header values must be nonempty printable ASCII")
        validate_tls_verification(self.verify)

    @property
    def action_url(self) -> str:
        """Return the normalized Action API base URL."""
        return self.site_url + self.action_path
