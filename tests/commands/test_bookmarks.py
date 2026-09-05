import httpx
import pytest

from readeck_cli.commands import CommandError, get_bookmark, get_share_link, list_bookmarks
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


BOOKMARK_SUMMARY = {
    "id": "abc123",
    "href": "/bookmarks/abc123",
    "created": "2024-01-01T00:00:00Z",
    "updated": "2024-01-01T00:00:00Z",
    "state": 0,
    "loaded": True,
    "url": "https://example.test/article",
    "title": "An article",
    "site_name": "Example",
    "site": "example.test",
    "published": "2024-01-01T00:00:00Z",
    "authors": ["Alice", "Bob"],
    "lang": "en",
    "text_direction": "ltr",
    "document_type": "article",
    "type": "article",
    "has_article": True,
    "description": "A description.",
    "note": "A note.",
    "is_deleted": False,
    "is_marked": False,
    "is_archived": False,
    "read_progress": 0,
    "labels": ["tech", "reading"],
    "word_count": 100,
    "reading_time": 1,
}


def test_list_bookmarks_maps_bookmark_summary_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks"
        return httpx.Response(200, json=[BOOKMARK_SUMMARY], headers={"Total-Count": "1", "Total-Pages": "1"})

    bookmarks, pagination_info = list_bookmarks(CREDENTIALS, transport=httpx.MockTransport(handler))

    assert len(bookmarks) == 1
    bookmark = bookmarks[0]
    assert bookmark.id == "abc123"
    assert bookmark.href == "/bookmarks/abc123"
    assert bookmark.url == "https://example.test/article"
    assert bookmark.title == "An article"
    assert bookmark.site == "example.test"
    assert bookmark.authors == ("Alice", "Bob")
    assert bookmark.description == "A description."
    assert bookmark.note == "A note."
    assert bookmark.labels == ("tech", "reading")
    assert pagination_info.total_count == 1
    assert pagination_info.total_pages == 1


def test_list_bookmarks_returns_empty_list_when_no_matches() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[], headers={"Total-Count": "0", "Total-Pages": "0"})

    bookmarks, pagination_info = list_bookmarks(CREDENTIALS, transport=httpx.MockTransport(handler))

    assert bookmarks == []
    assert pagination_info.total_count == 0


def test_list_bookmarks_passes_through_pagination_info_unchanged() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[], headers={"Total-Count": "42", "Total-Pages": "5"})

    _, pagination_info = list_bookmarks(CREDENTIALS, transport=httpx.MockTransport(handler))

    assert pagination_info.total_count == 42
    assert pagination_info.total_pages == 5


def test_list_bookmarks_forwards_search_and_pagination() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {"search": "python", "limit": "10", "offset": "5"}
        return httpx.Response(200, json=[])

    list_bookmarks(CREDENTIALS, search="python", limit=10, offset=5, transport=httpx.MockTransport(handler))


def test_list_bookmarks_wraps_client_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"is_valid": False, "errors": "invalid limit", "fields": {}})

    with pytest.raises(CommandError):
        list_bookmarks(CREDENTIALS, limit=-1, transport=httpx.MockTransport(handler))


def test_list_bookmarks_wraps_invalid_config() -> None:
    with pytest.raises(CommandError):
        list_bookmarks(ReadeckCredentials(base_url="", api_token="secret-token"))  # noqa: S106
