from importlib.metadata import version

from click.testing import CliRunner

from readeck_cli import main


def test_version_flag_prints_package_version() -> None:
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert version("readeck-cli") in result.output


def test_no_args_prints_usage() -> None:
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_h_flag_is_a_help_alias() -> None:
    result = CliRunner().invoke(main, ["-h"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
