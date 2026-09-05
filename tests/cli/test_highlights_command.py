import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from readeck_cli import main
from readeck_cli.commands import CommandError, Highlight
from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR


if TYPE_CHECKING:
    import pytest


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")


def test_highlights_get_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    result = CliRunner().invoke(main, ["highlights", "get", "abc"])

    assert result.exit_code == 2
    assert BASE_URL_ENV_VAR in result.output


def test_highlights_get_prints_human_readable_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    highlights = (Highlight(id="h1", created="2024-01-01", color="yellow", text="hi", note="a note"),)
    monkeypatch.setattr("readeck_cli.cli.highlights.get_highlights", lambda *_args, **_kwargs: highlights)

    result = CliRunner().invoke(main, ["highlights", "get", "abc"])

    assert result.exit_code == 0
    assert "id: h1" in result.output
    assert "created: 2024-01-01" in result.output
    assert "color: yellow" in result.output
    assert "text: hi" in result.output
    assert "note: a note" in result.output


def test_highlights_get_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    highlights = (Highlight(id="h1", created="2024-01-01", color="yellow", text="hi", note="a note"),)
    monkeypatch.setattr("readeck_cli.cli.highlights.get_highlights", lambda *_args, **_kwargs: highlights)

    result = CliRunner().invoke(main, ["highlights", "get", "abc", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {"id": "h1", "created": "2024-01-01", "color": "yellow", "text": "hi", "note": "a note"},
    ]


def test_highlights_get_empty_result_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.highlights.get_highlights", lambda *_args, **_kwargs: ())

    result = CliRunner().invoke(main, ["highlights", "get", "abc"])

    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_highlights_get_empty_result_json(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setattr("readeck_cli.cli.highlights.get_highlights", lambda *_args, **_kwargs: ())

    result = CliRunner().invoke(main, ["highlights", "get", "abc", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == []


def test_highlights_get_reports_command_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def raise_error(*_args: object, **_kwargs: object) -> tuple[Highlight, ...]:
        raise CommandError("unknown bookmark")

    monkeypatch.setattr("readeck_cli.cli.highlights.get_highlights", raise_error)

    result = CliRunner().invoke(main, ["highlights", "get", "unknown"])

    assert result.exit_code == 1
    assert "unknown bookmark" in result.output
