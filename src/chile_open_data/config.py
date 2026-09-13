"""Validated, immutable connection settings; constructors never read credentials implicitly."""

import re
from dataclasses import dataclass, field
from math import isfinite
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Configure a CKAN endpoint, timeouts in seconds, and connection pool limits.

    ``site_url`` can include a deployment prefix. TLS verification is enabled and
    redirects are deliberately disabled. ``api_token`` is excluded from repr.
    """

    site_url: str = "https://datos.gob.cl"
    action_path: str = "/api/3/action"
    api_token: str | None = field(default=None, repr=False)
    user_agent: str = "chile-open-data-sdk/0.1.0"
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    pool_timeout: float = 5.0
    max_connections: int = 100
    max_keepalive_connections: int = 20
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
        if not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+/?", self.action_path):
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
            isinstance(self.max_connections, bool)
            or not isinstance(self.max_connections, int)
            or self.max_connections < 1
            or isinstance(self.max_keepalive_connections, bool)
            or not isinstance(self.max_keepalive_connections, int)
            or not 0 <= self.max_keepalive_connections <= self.max_connections
        ):
            raise ValueError("Connection limits must be integers with 0 <= keepalive <= maximum")
        for header_value in (self.user_agent, self.api_token):
            if header_value is not None and (
                not header_value or any(ord(c) < 32 or ord(c) > 126 for c in header_value)
            ):
                raise ValueError("Header values must be nonempty printable ASCII")
        if not isinstance(self.verify, bool):
            raise ValueError("verify must be a boolean")

    @property
    def action_url(self) -> str:
        """Return the normalized Action API base URL."""
        return self.site_url + self.action_path
