import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from readeck_cli import main
from readeck_cli.commands import BookmarkDetails, BookmarkLink, CommandError
from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR


if TYPE_CHECKING:
    import pytest
    from pytest_regressions.file_regression import FileRegressionFixture


BOOKMARK = BookmarkDetails(
    id="abc123",
    href="https://example.test/readeck/api/bookmarks/abc123",
    url="https://example.test/article",
    title="Example",
    site="example.test",
    authors=("Jane Doe", "John Smith"),
    description="A short description",
    note="My note",
    labels=("reading", "tech"),
    links=(
        BookmarkLink(title="Related", url="https://example.test/related"),
        BookmarkLink(title="", url="https://example.test/further"),
    ),
)

EXPECTED_RECORD = {
    "id": "abc123",
    "href": "https://example.test/readeck/api/bookmarks/abc123",
    "url": "https://example.test/article",
    "title": "Example",
    "site": "example.test",
    "authors": ["Jane Doe", "John Smith"],
    "description": "A short description",
    "note": "My note",
    "labels": ["reading", "tech"],
    "links": [
        {"title": "Related", "url": "https://example.test/related"},
        {"title": "", "url": "https://example.test/further"},
    ],
}


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")


def test_bookmarks_get_requires_bookmark_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    result = CliRunner().invoke(main, ["bookmarks", "get"])

    assert result.exit_code == 2


def test_bookmarks_get_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    result = CliRunner().invoke(main, ["bookmarks", "get", "abc123"])

    assert result.exit_code == 2
    assert BASE_URL_ENV_VAR in result.output


def test_bookmarks_get_prints_human_readable_record(
    monkeypatch: pytest.MonkeyPatch, file_regression: FileRegressionFixture
) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_bookmark", lambda *_args, **_kwargs: BOOKMARK)

    result = CliRunner().invoke(main, ["bookmarks", "get", "abc123"])

    assert result.exit_code == 0
    file_regression.check(result.output, extension=".txt")


def test_bookmarks_get_human_output_omits_links_section_when_empty(
    monkeypatch: pytest.MonkeyPatch, file_regression: FileRegressionFixture
) -> None:
    _set_env(monkeypatch)
    bookmark = BookmarkDetails(
        id="xyz",
        href="",
        url="https://x.test",
        title="No Extras",
        site="x.test",
        authors=(),
        description="desc",
        note="",
        labels=(),
        links=(),
    )
    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_bookmark", lambda *_args, **_kwargs: bookmark)

    result = CliRunner().invoke(main, ["bookmarks", "get", "xyz"])

    assert result.exit_code == 0
    file_regression.check(result.output, extension=".txt")


def test_bookmarks_get_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_bookmark", lambda *_args, **_kwargs: BOOKMARK)

    result = CliRunner().invoke(main, ["bookmarks", "get", "abc123", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == [EXPECTED_RECORD]


def test_bookmarks_get_reports_command_errors_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def raise_error(*_args: object, **_kwargs: object) -> BookmarkDetails:
        raise CommandError("bookmark not found")

    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_bookmark", raise_error)

    result = CliRunner().invoke(main, ["bookmarks", "get", "missing"])

    assert result.exit_code == 1
    assert "bookmark not found" in result.output
    assert "Traceback" not in result.output
