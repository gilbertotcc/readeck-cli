from functools import cached_property

from readeck_cli.infrastructure.readeck_client.api.bookmark_collections_api import (
    BookmarkCollectionsApi,
)
from readeck_cli.infrastructure.readeck_client.api.bookmark_export_api import BookmarkExportApi
from readeck_cli.infrastructure.readeck_client.api.bookmark_highlights_api import BookmarkHighlightsApi
from readeck_cli.infrastructure.readeck_client.api.bookmark_import_api import BookmarkImportApi
from readeck_cli.infrastructure.readeck_client.api.bookmark_labels_api import BookmarkLabelsApi
from readeck_cli.infrastructure.readeck_client.api.bookmark_sharing_api import BookmarkSharingApi
from readeck_cli.infrastructure.readeck_client.api.bookmark_sync_api import BookmarkSyncApi
from readeck_cli.infrastructure.readeck_client.api.bookmarks_api import BookmarksApi
from readeck_cli.infrastructure.readeck_client.api.dev_tools_api import DevToolsApi
from readeck_cli.infrastructure.readeck_client.api.info_api import InfoApi
from readeck_cli.infrastructure.readeck_client.api.oauth_api import OauthApi
from readeck_cli.infrastructure.readeck_client.api.user_profile_api import UserProfileApi
from readeck_cli.infrastructure.readeck_client.api_client import ApiClient
from readeck_cli.infrastructure.readeck_client.configuration import Configuration


class ReadeckClient:
    """Configured access to the generated Readeck API client."""

    def __init__(self, *, host: str, token: str) -> None:
        configuration = Configuration(host=host, access_token=token)
        self._api_client = ApiClient(configuration)

    @property
    def api_client(self) -> ApiClient:
        return self._api_client

    @cached_property
    def bookmarks(self) -> BookmarksApi:
        return BookmarksApi(self._api_client)

    @cached_property
    def bookmark_collections(self) -> BookmarkCollectionsApi:
        return BookmarkCollectionsApi(self._api_client)

    @cached_property
    def bookmark_export(self) -> BookmarkExportApi:
        return BookmarkExportApi(self._api_client)

    @cached_property
    def bookmark_highlights(self) -> BookmarkHighlightsApi:
        return BookmarkHighlightsApi(self._api_client)

    @cached_property
    def bookmark_import(self) -> BookmarkImportApi:
        return BookmarkImportApi(self._api_client)

    @cached_property
    def bookmark_labels(self) -> BookmarkLabelsApi:
        return BookmarkLabelsApi(self._api_client)

    @cached_property
    def bookmark_sharing(self) -> BookmarkSharingApi:
        return BookmarkSharingApi(self._api_client)

    @cached_property
    def bookmark_sync(self) -> BookmarkSyncApi:
        return BookmarkSyncApi(self._api_client)

    @cached_property
    def dev_tools(self) -> DevToolsApi:
        return DevToolsApi(self._api_client)

    @cached_property
    def info(self) -> InfoApi:
        return InfoApi(self._api_client)

    @cached_property
    def oauth(self) -> OauthApi:
        return OauthApi(self._api_client)

    @cached_property
    def user_profile(self) -> UserProfileApi:
        return UserProfileApi(self._api_client)
