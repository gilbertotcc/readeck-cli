import httpx
import pytest

from readeck_cli.infrastructure.readeck_client import (
    PaginationParams,
    ReadeckClient,
    ReadeckClientConfig,
    ReadeckClientError,
)


BASE_URL = "http://example.test/readeck/api"
API_TOKEN = "secret-token"  # noqa: S105


def _config() -> ReadeckClientConfig:
    return ReadeckClientConfig.from_params(base_url=BASE_URL, api_token=API_TOKEN)


class _RaisingTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)


def test_get_info_returns_parsed_json() -> None:
    body = {"version": {"release": "1.2.3", "canonical": "1.2.3", "build": ""}, "features": ["oauth"]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/info"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_info() == body


def test_get_profile_sends_bearer_token_and_returns_json() -> None:
    body = {"provider": {"id": "token", "name": "API token", "permissions": []}, "user": {"username": "alice"}}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {API_TOKEN}"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_profile() == body


def test_get_share_link_returns_parsed_json_without_with_notes_param() -> None:
    body = {"url": "https://example.test/share/abc", "expires": "2026-01-01T00:00:00Z", "title": "Title", "id": "b1"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/b1/share/link"
        assert "with_notes" not in request.url.params
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_share_link("b1") == body


def test_get_share_link_sends_with_notes_query_param() -> None:
    body = {"url": "https://example.test/share/abc", "expires": "", "title": "", "id": "b1"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["with_notes"] == "true"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_share_link("b1", with_notes=True) == body


def test_get_share_link_raises_on_error_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "message": "not found"})

    with (
        ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_share_link("missing")

    assert exc_info.value.status_code == 404


def test_get_bookmark_returns_parsed_json() -> None:
    body = {"id": "abc123", "title": "Example", "url": "https://example.test/article"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/abc123"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_bookmark("abc123") == body


def test_get_profile_raises_on_401() -> None:
    body = {"status": 401, "message": "invalid token"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json=body)

    with (
        ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_profile()

    error = exc_info.value
    assert error.status_code == 401
    assert error.response_json() == body


def test_get_highlights_returns_parsed_json() -> None:
    body = [{"id": "abc", "created": "2024-01-01T00:00:00Z", "color": "yellow", "text": "hi", "note": "note"}]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/abc123/annotations"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_highlights("abc123") == body


def test_get_highlights_raises_on_404() -> None:
    body = {"status": 404, "message": "not found"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json=body)

    with (
        ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_highlights("unknown")

    assert exc_info.value.status_code == 404


def test_request_wraps_transport_error() -> None:
    with (
        ReadeckClient.from_config(_config(), transport=_RaisingTransport()) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_info()

    error = exc_info.value
    assert error.status_code is None
    assert error.response is None
    assert isinstance(error.__cause__, httpx.ConnectError)


def test_get_bookmarks_returns_parsed_list_and_pagination_info() -> None:
    body = [{"id": "abc", "title": "Example"}]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks"
        return httpx.Response(200, json=body, headers={"Total-Count": "137", "Total-Pages": "7"})

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        bookmarks, pagination_info = client.get_bookmarks()

    assert bookmarks == body
    assert pagination_info.total_count == 137
    assert pagination_info.total_pages == 7


def test_get_bookmarks_returns_empty_list_when_no_matches() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[], headers={"Total-Count": "0", "Total-Pages": "0"})

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        bookmarks, pagination_info = client.get_bookmarks()

    assert bookmarks == []
    assert pagination_info.total_count == 0


def test_get_bookmarks_sends_search_and_pagination_query_params() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {"search": "python", "limit": "10", "offset": "20"}
        return httpx.Response(200, json=[])

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        client.get_bookmarks(search="python", pagination=PaginationParams(limit=10, offset=20))


def test_get_bookmarks_omits_unset_query_params() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {}
        return httpx.Response(200, json=[])

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        client.get_bookmarks()


def test_get_bookmarks_omits_blank_search() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "search" not in request.url.params
        return httpx.Response(200, json=[])

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        client.get_bookmarks(search="")


def test_get_bookmarks_raises_on_422() -> None:
    body = {"is_valid": False, "errors": "invalid limit", "fields": {}}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json=body)

    with (
        ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_bookmarks(pagination=PaginationParams(limit=-1))

    assert exc_info.value.status_code == 422


def test_context_manager_closes_underlying_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    client = ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler))
    with client:
        pass

    with pytest.raises(RuntimeError, match="closed"):
        client.get_info()
