import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from readeck_cli import main
from readeck_cli.commands import CommandError, ShareLink
from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR


if TYPE_CHECKING:
    import pytest


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")


SHARE_LINK = ShareLink(url="https://example.test/share/abc", expires="2026-01-01T00:00:00Z", title="Title", id="b1")


def test_share_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1"])

    assert result.exit_code == 2
    assert BASE_URL_ENV_VAR in result.output


def test_share_prints_human_readable_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", lambda *_args, **_kwargs: SHARE_LINK)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1"])

    assert result.exit_code == 0
    assert f"url: {SHARE_LINK.url}" in result.output
    assert f"expires: {SHARE_LINK.expires}" in result.output
    assert f"title: {SHARE_LINK.title}" in result.output
    assert f"id: {SHARE_LINK.id}" in result.output


def test_share_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", lambda *_args, **_kwargs: SHARE_LINK)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {"url": SHARE_LINK.url, "expires": SHARE_LINK.expires, "title": SHARE_LINK.title, "id": SHARE_LINK.id},
    ]


def test_share_passes_with_notes_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    captured: dict[str, object] = {}

    def fake_get_share_link(_credentials: object, bookmark_id: str, *, with_notes: bool) -> ShareLink:
        captured["bookmark_id"] = bookmark_id
        captured["with_notes"] = with_notes
        return SHARE_LINK

    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", fake_get_share_link)

    result = CliRunner().invoke(main, ["bookmarks", "share", "--with-notes", "b1"])

    assert result.exit_code == 0
    assert captured == {"bookmark_id": "b1", "with_notes": True}


def test_share_with_notes_flag_after_bookmark_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    captured: dict[str, object] = {}

    def fake_get_share_link(_credentials: object, bookmark_id: str, *, with_notes: bool) -> ShareLink:
        captured["bookmark_id"] = bookmark_id
        captured["with_notes"] = with_notes
        return SHARE_LINK

    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", fake_get_share_link)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1", "--with-notes"])

    assert result.exit_code == 0
    assert captured == {"bookmark_id": "b1", "with_notes": True}


def test_share_without_with_notes_defaults_false(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    captured: dict[str, object] = {}

    def fake_get_share_link(_credentials: object, bookmark_id: str, *, with_notes: bool) -> ShareLink:
        captured["with_notes"] = with_notes
        return SHARE_LINK

    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", fake_get_share_link)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1"])

    assert result.exit_code == 0
    assert captured == {"with_notes": False}


def test_share_requires_bookmark_id_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    result = CliRunner().invoke(main, ["bookmarks", "share"])

    assert result.exit_code == 2
    assert "BOOKMARK_ID" in result.output


def test_share_reports_command_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def raise_error(*_args: object, **_kwargs: object) -> ShareLink:
        raise CommandError("boom")

    monkeypatch.setattr("readeck_cli.cli.bookmarks.get_share_link", raise_error)

    result = CliRunner().invoke(main, ["bookmarks", "share", "b1"])

    assert result.exit_code == 1
    assert "boom" in result.output


def test_share_help_shows_options() -> None:
    result = CliRunner().invoke(main, ["bookmarks", "share", "--help"])

    assert result.exit_code == 0
    assert "BOOKMARK_ID" in result.output
    assert "--with-notes" in result.output
    assert "--json" in result.output
