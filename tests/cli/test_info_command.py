import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from readeck_cli import main
from readeck_cli.commands import CommandError, InstanceInfo
from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR


if TYPE_CHECKING:
    import pytest
    from pytest_regressions.file_regression import FileRegressionFixture


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")


def test_info_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    result = CliRunner().invoke(main, ["info"])

    assert result.exit_code == 2
    assert BASE_URL_ENV_VAR in result.output


def test_info_prints_human_readable_summary(
    monkeypatch: pytest.MonkeyPatch, file_regression: FileRegressionFixture
) -> None:
    _set_env(monkeypatch)
    info = InstanceInfo(release="0.23.2", canonical="0.23.2", build="", features=("email", "oauth"))
    monkeypatch.setattr("readeck_cli.cli.info.get_instance_info", lambda *_args, **_kwargs: info)

    result = CliRunner().invoke(main, ["info"])

    assert result.exit_code == 0
    file_regression.check(result.output, extension=".txt")


def test_info_prints_nightly_build_label(
    monkeypatch: pytest.MonkeyPatch, file_regression: FileRegressionFixture
) -> None:
    _set_env(monkeypatch)
    info = InstanceInfo(release="0.24.0", canonical="0.24.0-175-g154ad5c1", build="175-g154ad5c1", features=())
    monkeypatch.setattr("readeck_cli.cli.info.get_instance_info", lambda *_args, **_kwargs: info)

    result = CliRunner().invoke(main, ["info"])

    assert result.exit_code == 0
    file_regression.check(result.output, extension=".txt")


def test_info_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    info = InstanceInfo(release="0.23.2", canonical="0.23.2", build="", features=("email",))
    monkeypatch.setattr("readeck_cli.cli.info.get_instance_info", lambda *_args, **_kwargs: info)

    result = CliRunner().invoke(main, ["info", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "version": "0.23.2",
        "kind": "stable",
        "features": ["email"],
    }


def test_info_reports_command_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def raise_error(*_args: object, **_kwargs: object) -> InstanceInfo:
        raise CommandError("boom")

    monkeypatch.setattr("readeck_cli.cli.info.get_instance_info", raise_error)

    result = CliRunner().invoke(main, ["info"])

    assert result.exit_code == 1
    assert "boom" in result.output
