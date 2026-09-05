import click
import pytest

from readeck_cli.config import BASE_URL_ENV_VAR, TOKEN_ENV_VAR, load_credentials


def test_load_credentials_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, " http://example.test/readeck/api ")
    monkeypatch.setenv(TOKEN_ENV_VAR, " secret-token ")

    credentials = load_credentials()

    assert credentials.base_url == "http://example.test/readeck/api"
    assert credentials.api_token == "secret-token"  # noqa: S105


def test_load_credentials_raises_on_missing_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BASE_URL_ENV_VAR, raising=False)
    monkeypatch.setenv(TOKEN_ENV_VAR, "secret-token")

    with pytest.raises(click.UsageError, match=BASE_URL_ENV_VAR):
        load_credentials()


def test_load_credentials_raises_on_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BASE_URL_ENV_VAR, "http://example.test/readeck/api")
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

    with pytest.raises(click.UsageError, match=TOKEN_ENV_VAR):
        load_credentials()
