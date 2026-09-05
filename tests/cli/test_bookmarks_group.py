from click.testing import CliRunner

from readeck_cli import main


def test_bookmarks_help_shows_group() -> None:
    result = CliRunner().invoke(main, ["bookmarks", "--help"])

    assert result.exit_code == 0
    assert "Manage Readeck bookmarks." in result.output


def test_bookmarks_without_subcommand_prints_help() -> None:
    result = CliRunner().invoke(main, ["bookmarks"])

    assert result.exit_code == 0
    assert "Manage Readeck bookmarks." in result.output
