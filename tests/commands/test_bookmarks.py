import httpx
import pytest

from readeck_cli.commands import CommandError, get_share_link
from readeck_cli.config import ReadeckCredentials


CREDENTIALS = ReadeckCredentials(base_url="http://example.test/readeck/api", api_token="secret-token")  # noqa: S106


def test_get_share_link_parses_response() -> None:
    body = {"url": "https://example.test/share/abc", "expires": "2026-01-01T00:00:00Z", "title": "Title", "id": "b1"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/b1/share/link"
        return httpx.Response(200, json=body)

    share_link = get_share_link(CREDENTIALS, "b1", transport=httpx.MockTransport(handler))

    assert share_link.url == body["url"]
    assert share_link.expires == body["expires"]
    assert share_link.title == body["title"]
    assert share_link.id == body["id"]


def test_get_share_link_passes_with_notes_flag() -> None:
    body = {"url": "", "expires": "", "title": "", "id": "b1"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["with_notes"] == "true"
        return httpx.Response(200, json=body)

    get_share_link(CREDENTIALS, "b1", with_notes=True, transport=httpx.MockTransport(handler))


def test_get_share_link_omits_with_notes_by_default() -> None:
    body = {"url": "", "expires": "", "title": "", "id": "b1"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert "with_notes" not in request.url.params
        return httpx.Response(200, json=body)

    get_share_link(CREDENTIALS, "b1", transport=httpx.MockTransport(handler))


def test_get_share_link_wraps_client_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "message": "not found"})

    with pytest.raises(CommandError):
        get_share_link(CREDENTIALS, "missing", transport=httpx.MockTransport(handler))


def test_get_share_link_wraps_invalid_config() -> None:
    with pytest.raises(CommandError):
        get_share_link(ReadeckCredentials(base_url="", api_token="secret-token"), "b1")  # noqa: S106
