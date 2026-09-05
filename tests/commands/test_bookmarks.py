import httpx
import pytest

from readeck_cli.commands import CommandError, get_bookmark, get_share_link
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


def test_get_bookmark_parses_full_payload() -> None:
    body = {
        "id": "abc123",
        "href": "https://example.test/readeck/api/bookmarks/abc123",
        "url": "https://example.test/article",
        "title": "Example",
        "site": "example.test",
        "authors": ["Jane Doe"],
        "description": "A short description",
        "note": "My note",
        "labels": ["reading"],
        "links": [{"title": "Related", "url": "https://example.test/related", "domain": "example.test"}],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/abc123"
        return httpx.Response(200, json=body)

    bookmark = get_bookmark("abc123", CREDENTIALS, transport=httpx.MockTransport(handler))

    assert bookmark.id == "abc123"
    assert bookmark.href == body["href"]
    assert bookmark.url == body["url"]
    assert bookmark.title == "Example"
    assert bookmark.site == "example.test"
    assert bookmark.authors == ("Jane Doe",)
    assert bookmark.description == "A short description"
    assert bookmark.note == "My note"
    assert bookmark.labels == ("reading",)
    assert len(bookmark.links) == 1
    assert bookmark.links[0].title == "Related"
    assert bookmark.links[0].url == "https://example.test/related"


def test_get_bookmark_defaults_missing_list_fields_to_empty() -> None:
    body = {"id": "abc123", "title": "Example"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    bookmark = get_bookmark("abc123", CREDENTIALS, transport=httpx.MockTransport(handler))

    assert bookmark.authors == ()
    assert bookmark.labels == ()
    assert bookmark.links == ()


def test_get_bookmark_surfaces_api_error_message() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "message": "bookmark not found"})

    with pytest.raises(CommandError, match="bookmark not found"):
        get_bookmark("missing", CREDENTIALS, transport=httpx.MockTransport(handler))


def test_get_bookmark_falls_back_to_generic_message_without_api_message() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    with pytest.raises(CommandError, match="returned 404"):
        get_bookmark("missing", CREDENTIALS, transport=httpx.MockTransport(handler))


def test_get_bookmark_wraps_invalid_config() -> None:
    with pytest.raises(CommandError):
        get_bookmark("abc123", ReadeckCredentials(base_url="", api_token="secret-token"))  # noqa: S106
