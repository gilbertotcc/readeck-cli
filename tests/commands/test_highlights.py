import httpx
import pytest

from readeck_cli.commands import CommandError, get_highlights
from readeck_cli.config import ReadeckCredentials


CREDENTIALS = ReadeckCredentials(base_url="http://example.test/readeck/api", api_token="secret-token")  # noqa: S106


def test_get_highlights_parses_full_annotation() -> None:
    body = [{"id": "abc", "created": "2024-01-01T00:00:00Z", "color": "yellow", "text": "hi", "note": "a note"}]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/bookmarks/abc/annotations"
        return httpx.Response(200, json=body)

    highlights = get_highlights(CREDENTIALS, "abc", transport=httpx.MockTransport(handler))

    assert len(highlights) == 1
    highlight = highlights[0]
    assert highlight.id == "abc"
    assert highlight.created == "2024-01-01T00:00:00Z"
    assert highlight.color == "yellow"
    assert highlight.text == "hi"
    assert highlight.note == "a note"


def test_get_highlights_defaults_missing_color_and_note_to_blank() -> None:
    body = [{"id": "abc", "created": "2024-01-01T00:00:00Z", "text": "hi"}]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    highlights = get_highlights(CREDENTIALS, "abc", transport=httpx.MockTransport(handler))

    assert len(highlights) == 1
    highlight = highlights[0]
    assert highlight.color == ""
    assert highlight.note == ""


def test_get_highlights_empty_list_is_not_an_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    highlights = get_highlights(CREDENTIALS, "abc", transport=httpx.MockTransport(handler))

    assert highlights == ()


def test_get_highlights_wraps_client_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "message": "not found"})

    with pytest.raises(CommandError):
        get_highlights(CREDENTIALS, "unknown", transport=httpx.MockTransport(handler))


def test_get_highlights_wraps_invalid_config() -> None:
    with pytest.raises(CommandError):
        get_highlights(ReadeckCredentials(base_url="", api_token="secret-token"), "abc")  # noqa: S106
