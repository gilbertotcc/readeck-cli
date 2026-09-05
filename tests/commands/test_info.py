import httpx
import pytest

from readeck_cli.commands import CommandError, get_instance_info
from readeck_cli.config import ReadeckCredentials


CREDENTIALS = ReadeckCredentials(base_url="http://example.test/readeck/api", api_token="secret-token")  # noqa: S106


def test_get_instance_info_parses_stable_release() -> None:
    body = {"version": {"release": "0.23.2", "canonical": "0.23.2", "build": ""}, "features": ["email", "oauth"]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/info"
        return httpx.Response(200, json=body)

    info = get_instance_info(CREDENTIALS, transport=httpx.MockTransport(handler))

    assert info.release == "0.23.2"
    assert info.canonical == "0.23.2"
    assert info.build == ""
    assert info.features == ("email", "oauth")
    assert info.is_nightly is False


def test_get_instance_info_parses_nightly_build() -> None:
    body = {
        "version": {"release": "0.24.0", "canonical": "0.24.0-175-g154ad5c1", "build": "175-g154ad5c1"},
        "features": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    info = get_instance_info(CREDENTIALS, transport=httpx.MockTransport(handler))

    assert info.build == "175-g154ad5c1"
    assert info.features == ()
    assert info.is_nightly is True


def test_get_instance_info_wraps_client_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"status": 401, "message": "invalid token"})

    with pytest.raises(CommandError):
        get_instance_info(CREDENTIALS, transport=httpx.MockTransport(handler))


def test_get_instance_info_wraps_invalid_config() -> None:
    with pytest.raises(CommandError):
        get_instance_info(ReadeckCredentials(base_url="", api_token="secret-token"))  # noqa: S106
