from click.testing import CliRunner

from readeck_cli import main


def test_highlights_help_shows_group() -> None:
    result = CliRunner().invoke(main, ["highlights", "--help"])

    assert result.exit_code == 0
    assert "Manage Readeck highlights." in result.output


def test_highlights_without_subcommand_prints_help() -> None:
    result = CliRunner().invoke(main, ["highlights"])

    assert result.exit_code == 0
    assert "Manage Readeck highlights." in result.output
