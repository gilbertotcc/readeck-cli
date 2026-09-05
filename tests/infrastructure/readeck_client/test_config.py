import pytest

from readeck_cli.infrastructure.readeck_client import ReadeckClientConfig


API_TOKEN = "secret-token"  # noqa: S105


def test_strips_trailing_slash_from_base_url() -> None:
    config = ReadeckClientConfig.from_params(base_url="http://example.test/readeck/api/", api_token=API_TOKEN)

    assert config.base_url == "http://example.test/readeck/api"


def test_default_timeout() -> None:
    config = ReadeckClientConfig.from_params(base_url="http://example.test/readeck/api", api_token=API_TOKEN)

    assert config.timeout == 10.0


def test_rejects_empty_base_url() -> None:
    with pytest.raises(ValueError, match="base_url"):
        ReadeckClientConfig.from_params(base_url="  ", api_token=API_TOKEN)


def test_rejects_empty_api_token() -> None:
    with pytest.raises(ValueError, match="api_token"):
        ReadeckClientConfig.from_params(base_url="http://example.test/readeck/api", api_token="")
