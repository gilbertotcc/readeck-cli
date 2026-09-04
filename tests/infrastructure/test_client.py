from readeck_cli.infrastructure.client import ReadeckClient
from readeck_cli.infrastructure.readeck_client.api.bookmarks_api import BookmarksApi
from readeck_cli.infrastructure.readeck_client.api.user_profile_api import UserProfileApi


def test_configures_host_and_bearer_token() -> None:
    client = ReadeckClient(host="http://example.test/readeck/api", token="secret-token")

    assert client.api_client.configuration.host == "http://example.test/readeck/api"
    assert client.api_client.configuration.access_token == "secret-token"


def test_exposes_typed_api_accessors() -> None:
    client = ReadeckClient(host="http://example.test/readeck/api", token="secret-token")

    assert isinstance(client.bookmarks, BookmarksApi)
    assert isinstance(client.user_profile, UserProfileApi)


def test_api_accessors_are_memoized() -> None:
    client = ReadeckClient(host="http://example.test/readeck/api", token="secret-token")

    assert client.bookmarks is client.bookmarks
    assert client.user_profile is client.user_profile


def test_api_accessors_share_the_same_api_client() -> None:
    client = ReadeckClient(host="http://example.test/readeck/api", token="secret-token")

    assert client.bookmarks.api_client is client.api_client
    assert client.user_profile.api_client is client.api_client
    assert client.bookmark_collections.api_client is client.api_client
    assert client.bookmark_export.api_client is client.api_client
    assert client.bookmark_highlights.api_client is client.api_client
    assert client.bookmark_import.api_client is client.api_client
    assert client.bookmark_labels.api_client is client.api_client
    assert client.bookmark_sharing.api_client is client.api_client
    assert client.bookmark_sync.api_client is client.api_client
    assert client.dev_tools.api_client is client.api_client
    assert client.info.api_client is client.api_client
    assert client.oauth.api_client is client.api_client
