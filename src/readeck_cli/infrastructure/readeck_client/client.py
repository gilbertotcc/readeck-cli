from typing import TYPE_CHECKING, Any, Self, cast

import httpx

from readeck_cli.infrastructure.readeck_client.errors import ReadeckClientError
from readeck_cli.infrastructure.readeck_client.pagination import PaginationInfo


if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

    from readeck_cli.infrastructure.readeck_client.config import ReadeckClientConfig
    from readeck_cli.infrastructure.readeck_client.pagination import PaginationParams


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

    def get_share_link(self, bookmark_id: str, *, with_notes: bool = False) -> dict[str, Any]:
        """`GET /bookmarks/{id}/share/link` — a public share link for a bookmark."""
        params = {"with_notes": "true"} if with_notes else None
        return cast(
            "dict[str, Any]",
            self._request("GET", f"/bookmarks/{bookmark_id}/share/link", params=params),
        )

    def get_highlights(self, bookmark_id: str) -> list[dict[str, Any]]:
        """`GET /bookmarks/{id}/annotations` — a bookmark's highlights."""
        return cast("list[dict[str, Any]]", self._request("GET", f"/bookmarks/{bookmark_id}/annotations"))

    def get_bookmark(self, bookmark_id: str) -> dict[str, Any]:
        """`GET /bookmarks/{id}` — a single bookmark's full details."""
        return cast("dict[str, Any]", self._request("GET", f"/bookmarks/{bookmark_id}"))

    def get_bookmarks(
        self,
        *,
        search: str | None = None,
        pagination: PaginationParams | None = None,
    ) -> tuple[list[dict[str, Any]], PaginationInfo]:
        """`GET /bookmarks` — a paginated bookmark list, paired with its pagination metadata."""
        params: dict[str, Any] = pagination.to_query_params() if pagination is not None else {}
        if search:
            params["search"] = search

        response = self._send("GET", "/bookmarks", params=params)
        body = cast("list[dict[str, Any]]", self._parse_json("GET", "/bookmarks", response))
        return body, PaginationInfo.from_headers(response.headers)

    def _request(self, method: str, path: str, *, params: Mapping[str, Any] | None = None) -> Any:
        return self._parse_json(method, path, self._send(method, path, params=params))

    def _send(self, method: str, path: str, *, params: Mapping[str, Any] | None = None) -> httpx.Response:
        try:
            response = self._http.request(method, path, params=params)
        except httpx.HTTPError as exc:
            message = f"{method} {path} failed: {exc}"
            raise ReadeckClientError(message, request=exc.request) from exc

        if response.is_error:
            message = f"{method} {path} returned {response.status_code}"
            raise ReadeckClientError(message, request=response.request, response=response)

        return response

    def _parse_json(self, method: str, path: str, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            message = f"{method} {path} returned a non-JSON body"
            raise ReadeckClientError(message, request=response.request, response=response) from exc
