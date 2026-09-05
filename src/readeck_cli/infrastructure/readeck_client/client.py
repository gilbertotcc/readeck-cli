from typing import TYPE_CHECKING, Any, Self, cast

import httpx

from readeck_cli.infrastructure.readeck_client.errors import ReadeckClientError


if TYPE_CHECKING:
    from types import TracebackType

    from readeck_cli.infrastructure.readeck_client.config import ReadeckClientConfig


class ReadeckClient:
    """A token-authenticated HTTP client for the Readeck API."""

    def __init__(
        self,
        config: ReadeckClientConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={"Authorization": f"Bearer {config.api_token}"},
            transport=transport,
        )

    @classmethod
    def from_config(cls, config: ReadeckClientConfig, *, transport: httpx.BaseTransport | None = None) -> Self:
        return cls(config, transport=transport)

    def __enter__(self) -> ReadeckClient:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def get_info(self) -> dict[str, Any]:
        """`GET /info` — public information about the Readeck instance."""
        return cast("dict[str, Any]", self._request("GET", "/info"))

    def get_profile(self) -> dict[str, Any]:
        """`GET /profile` — the current user's profile information."""
        return cast("dict[str, Any]", self._request("GET", "/profile"))

    def _request(self, method: str, path: str) -> Any:
        try:
            response = self._http.request(method, path)
        except httpx.HTTPError as exc:
            message = f"{method} {path} failed: {exc}"
            raise ReadeckClientError(message, request=exc.request) from exc

        if response.is_error:
            message = f"{method} {path} returned {response.status_code}"
            raise ReadeckClientError(message, request=response.request, response=response)

        try:
            return response.json()
        except ValueError as exc:
            message = f"{method} {path} returned a non-JSON body"
            raise ReadeckClientError(message, request=response.request, response=response) from exc
