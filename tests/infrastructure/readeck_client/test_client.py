import httpx
import pytest

from readeck_cli.infrastructure.readeck_client import ReadeckClient, ReadeckClientConfig, ReadeckClientError


BASE_URL = "http://example.test/readeck/api"
API_TOKEN = "secret-token"  # noqa: S105


def _config() -> ReadeckClientConfig:
    return ReadeckClientConfig.from_params(base_url=BASE_URL, api_token=API_TOKEN)


class _RaisingTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)


def test_get_info_returns_parsed_json() -> None:
    body = {"version": {"release": "1.2.3", "canonical": "1.2.3", "build": ""}, "features": ["oauth"]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readeck/api/info"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_info() == body


def test_get_profile_sends_bearer_token_and_returns_json() -> None:
    body = {"provider": {"id": "token", "name": "API token", "permissions": []}, "user": {"username": "alice"}}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {API_TOKEN}"
        return httpx.Response(200, json=body)

    with ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client:
        assert client.get_profile() == body


def test_get_profile_raises_on_401() -> None:
    body = {"status": 401, "message": "invalid token"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json=body)

    with (
        ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_profile()

    error = exc_info.value
    assert error.status_code == 401
    assert error.response_json() == body


def test_request_wraps_transport_error() -> None:
    with (
        ReadeckClient.from_config(_config(), transport=_RaisingTransport()) as client,
        pytest.raises(ReadeckClientError) as exc_info,
    ):
        client.get_info()

    error = exc_info.value
    assert error.status_code is None
    assert error.response is None
    assert isinstance(error.__cause__, httpx.ConnectError)


def test_context_manager_closes_underlying_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    client = ReadeckClient.from_config(_config(), transport=httpx.MockTransport(handler))
    with client:
        pass

    with pytest.raises(RuntimeError, match="closed"):
        client.get_info()
