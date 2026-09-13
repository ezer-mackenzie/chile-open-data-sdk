"""Synchronous CKAN clients and generic JSON Action API access."""

import json
import re
from collections.abc import Mapping
from types import TracebackType
from typing import Self

import httpx

from chile_open_data._internal.responses import parse_response, redact
from chile_open_data.config import ClientConfig
from chile_open_data.errors import CKANConnectionError, CKANError, CKANTimeoutError
from chile_open_data.types import JSONValue


class ActionService:
    """Generic CKAN JSON actions, with no automatic retries or redirects."""

    def __init__(self, http: httpx.Client, config: ClientConfig) -> None:
        self._http = http
        self._config = config

    def call(self, action: str, data: Mapping[str, JSONValue] | None = None) -> JSONValue:
        """POST action parameters as JSON and return the unwrapped result.

        Action names must be single alphanumeric/underscore identifiers. Calls
        may mutate server data: choose actions and credentials deliberately.
        Unsupported payload values raise ValueError before any network request.
        """
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", action):
            raise ValueError("action must be a CKAN action identifier")
        safe_action = str(redact(action, self._config.api_token))
        if self._http.is_closed:
            raise CKANError("Client is closed", action=safe_action)
        try:
            payload = json.dumps(dict(data) if data is not None else {}, allow_nan=False)
        except (TypeError, ValueError):
            raise ValueError("data must be a JSON-compatible mapping with finite numbers") from None
        # Suppress raw HTTPX exception messages and chains, which can contain credentials.
        failure: CKANError | None = None
        try:
            response = self._http.post(
                self._config.action_url + "/" + action, content=payload.encode("utf-8")
            )
        except httpx.TimeoutException:
            failure = CKANTimeoutError("CKAN request timed out", action=safe_action)
        except httpx.RequestError:
            failure = CKANConnectionError("CKAN request could not complete", action=safe_action)
        if failure is not None:
            raise failure
        return parse_response(response, safe_action, self._config.api_token)


class CKANClient:
    """Reusable synchronous client for an explicitly configured CKAN site.

    Supply either ``site_url`` (and optionally ``api_token``) or ``config``.
    An injected HTTPX transport is owned and closed by this client.
    """

    def __init__(
        self,
        site_url: str | None = None,
        *,
        api_token: str | None = None,
        config: ClientConfig | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if config is not None and (site_url is not None or api_token is not None):
            raise ValueError("Pass config or site_url/api_token, not both")
        if config is None:
            if site_url is None:
                raise ValueError("CKANClient requires site_url or config")
            config = ClientConfig(site_url=site_url, api_token=api_token)
        self.config = config
        headers = {
            "User-Agent": config.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if config.api_token is not None:
            headers["Authorization"] = config.api_token
        self._http = httpx.Client(
            headers=headers,
            timeout=httpx.Timeout(
                connect=config.connect_timeout,
                read=config.read_timeout,
                write=config.write_timeout,
                pool=config.pool_timeout,
            ),
            limits=httpx.Limits(
                max_connections=config.max_connections,
                max_keepalive_connections=config.max_keepalive_connections,
            ),
            verify=config.verify,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )
        self.actions = ActionService(self._http, config)

    @property
    def is_closed(self) -> bool:
        """Whether the owned HTTP client has been closed."""
        return self._http.is_closed

    def close(self) -> None:
        """Release the connection pool; safe to call more than once."""
        self._http.close()

    def __enter__(self) -> Self:
        if self.is_closed:
            raise CKANError("Client is closed", action="")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class ChileOpenDataClient(CKANClient):
    """CKAN client defaulting to https://datos.gob.cl/api/3/action."""

    def __init__(
        self,
        site_url: str | None = None,
        *,
        api_token: str | None = None,
        config: ClientConfig | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__(
            site_url="https://datos.gob.cl" if config is None and site_url is None else site_url,
            api_token=api_token,
            config=config,
            transport=transport,
        )
