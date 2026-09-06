import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from readeck_cli import main
from readeck_cli.commands import Bookmark, CommandError, PaginationInfo
from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR


if TYPE_CHECKING:
    import pytest

BOOKMARK = Bookmark(
    id="abc123",
    href="/bookmarks/abc123",
    url="https://example.test/article",
    title="An article",
    site="example.test",
    authors=("Alice", "Bob"),
    description="A description.",
    note="A note.",
    labels=("tech", "reading"),
)


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")


def _stub_list_bookmarks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bookmarks: list[Bookmark],
    pagination_info: PaginationInfo,
    captured: dict[str, object] | None = None,
) -> None:
    def fake_list_bookmarks(_credentials: object, **kwargs: object) -> tuple[list[Bookmark], PaginationInfo]:
        if captured is not None:
            captured.update(kwargs)
        return bookmarks, pagination_info

    monkeypatch.setattr("readeck_cli.cli.bookmarks.list_bookmarks", fake_list_bookmarks)


def test_list_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 2
    assert BASE_URL_ENV_VAR in result.output


def test_list_help(monkeypatch: pytest.MonkeyPatch) -> None:
    result = CliRunner().invoke(main, ["bookmarks", "list", "--help"])

    assert result.exit_code == 0
    assert "SEARCH" in result.output


def test_list_prints_human_readable_records(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[BOOKMARK], pagination_info=PaginationInfo(total_count=1, total_pages=1)
    )

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 0
    assert result.stdout == (
        "An article\n"
        "  ID:          abc123\n"
        "  URL:         https://example.test/article\n"
        "  Site:        example.test\n"
        "  Authors:     Alice, Bob\n"
        "  Labels:      tech, reading\n"
        "  Description: A description.\n"
        "  Note:        A note.\n"
    )


def test_list_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[BOOKMARK], pagination_info=PaginationInfo(total_count=1, total_pages=1)
    )

    result = CliRunner().invoke(main, ["bookmarks", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == [
        {
            "id": "abc123",
            "href": "/bookmarks/abc123",
            "url": "https://example.test/article",
            "title": "An article",
            "site": "example.test",
            "authors": ["Alice", "Bob"],
            "description": "A description.",
            "note": "A note.",
            "labels": ["tech", "reading"],
        }
    ]


def test_list_empty_result_human(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(monkeypatch, bookmarks=[], pagination_info=PaginationInfo(total_count=0, total_pages=0))

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 0
    assert result.stdout == "No bookmarks found.\n"


def test_list_empty_result_json(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(monkeypatch, bookmarks=[], pagination_info=PaginationInfo(total_count=0, total_pages=0))

    result = CliRunner().invoke(main, ["bookmarks", "list", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


def test_list_prints_pagination_summary_when_multiple_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[BOOKMARK], pagination_info=PaginationInfo(total_count=42, total_pages=5)
    )

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 0
    assert "1 of 42 across 5 page(s)" in result.stderr


def test_list_prints_pagination_summary_in_json_mode_too(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[BOOKMARK], pagination_info=PaginationInfo(total_count=42, total_pages=5)
    )

    result = CliRunner().invoke(main, ["bookmarks", "list", "--json"])

    assert result.exit_code == 0
    assert "1 of 42 across 5 page(s)" in result.stderr
    assert json.loads(result.stdout)


def test_list_omits_pagination_summary_for_single_page(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[BOOKMARK], pagination_info=PaginationInfo(total_count=1, total_pages=1)
    )

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 0
    assert result.stderr == ""


def test_list_forwards_search_and_pagination_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    captured: dict[str, object] = {}
    _stub_list_bookmarks(
        monkeypatch, bookmarks=[], pagination_info=PaginationInfo(total_count=0, total_pages=0), captured=captured
    )

    result = CliRunner().invoke(main, ["bookmarks", "list", "python", "--limit", "10", "--offset", "5"])

    assert result.exit_code == 0
    assert captured == {"search": "python", "limit": 10, "offset": 5}


def test_list_reports_command_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def raise_error(*_args: object, **_kwargs: object) -> tuple[list[Bookmark], PaginationInfo]:
        raise CommandError("boom")

    monkeypatch.setattr("readeck_cli.cli.bookmarks.list_bookmarks", raise_error)

    result = CliRunner().invoke(main, ["bookmarks", "list"])

    assert result.exit_code == 1
    assert "boom" in result.stderr
