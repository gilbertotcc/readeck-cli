"""
    Readeck API

    # Introduction  The Readeck API provides REST endpoints that can be used for any purpose, should it be a mobile application, a script, you name it.  ## API Endpoint  You can access this API on `http://10.254.10.7/readeck/api`.  Most of your requests and responses are using JSON as the exchange format.  ## Test the API  On this documentation, you can test every route.  If you don't provide an API token in [Authentication](#auth), you can still test all the routes but note that the given curl examples only work with an API token.  # Token Authentication  If you're writing a script for yourself, the easiest way is to [generate an API token](../profile/tokens) that you can use using the `Bearer` HTTP authorization scheme.  For example, you first request will look like:  ```sh curl -H \"Authorization: Bearer <TOKEN>\" http://10.254.10.7/readeck/api/profile ```  Or, in NodeJS:  ```js fetch(\"http://10.254.10.7/readeck/api/profile\", {     headers: {     \"Authorization\": \"Bearer <TOKEN>\",     }, }) ```   # Authentication with OAuth  If you're writing an application that requires a user to grant the application permission to access their Readeck instance, you should not ask a user to create an API Token but instead, implement the necessary OAuth flow so that your application can retrieve a token in a user friendly way.  ## Available Scopes  An OAuth token grants the application some permissions based on the requested scopes. This are the available scopes you can request:  | Name              | Description                    | | :---------------- | ------------------------------ | | `bookmarks:read`  | Read only access to bookmarks  | | `bookmarks:write` | Write only access to bookmarks | | `profile:read`    | Extended profile information   |  You can see which scope applies on each route of this documentation. A route without a scope (and not \"public\") is not available with an OAuth token.  ## Client Registration  Before you can start the authorization flow, you first need to register a client on the Readeck instance.  <details> <summary>Client Registration Flow</summary> <pre role=\"img\" aria-label=\"Client Registration sequence diagram\">  ┌──────┐                 ┌────────────┐  │Client│                 │Registration│  └──┬───┘                 └─────┬──────┘     │                           │     │Client Registration Request│     │POST /api/oauth/client     │     │──────────────────────────>│     │                           │     │Client Information Response│     │<──────────────────────────│  ┌──┴───┐                 ┌─────┴──────┐  │Client│                 │Registration│  └──────┘                 └────────────┘ </pre> </details>  Readeck implement [OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591). You can register a client by querying the [Client Creation Route](#post-/oauth/client).  Upon registration, you'll receive a `client_id` that you can use in the next authorization step.  Unlike more traditional client implementations, Readeck OAuth clients are ephemeral:  - You **must** register a new client each time you start an authorization flow. - The Client is valid for 10 minutes after creation.  ## OAuth Authorization Code Flow  The Authorization Code Flow is used by clients to exchange an authorization code for an access token.  After the user returns to the client via the redirect URL, the application will get the authorization code from the URL and use it to request an access token.  This flow can only be used when, on the same device, the client can:  - send the user to the authorization page - process the redirect URL to retrieve the authorization code  On a device without a browser, a client can use the [Device Code Flow](#overview--oauth-device-code-flow).  <details> <summary>Authorization Code Flow</summary>  <pre role=\"img\" aria-label=\"Authorization Code sequence diagram\">  ┌────┐            ┌──────┐                               ┌─────────────┐      ┌───┐  │User│            │Client│                               │Authorization│      │API│  └─┬──┘            └──┬───┘                               └──────┬──────┘      └─┬─┘    │                  │                                          │               │    │Enter instance URL│                                          │               │    │─────────────────>│                                          │               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Generate PKCE verifier and challenge  │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │        Open Authorization URL            │               │    │                  │        GET /authorize?...                │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │         Redirect to login/authorization prompt              │               │    │<────────────────────────────────────────────────────────────│               │    │                  │                                          │               │    │Authorize Client                                             │               │    │POST /authorize?...                                          │               │    │────────────────────────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │          Authorization Code              │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Check state                           │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │Request Token (with code and verifier)    │               │    │                  │POST /api/oauth/token                     │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │                                          │──┐            │    │                  │                                          │  │ Check PKCE │    │                  │                                          │<─┘            │    │                  │                                          │               │    │                  │             Access Token                 │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │         Request data with Access Token   │               │    │                  │─────────────────────────────────────────────────────────>│    │                  │                                          │               │    │                  │                    Response              │               │    │                  │<─────────────────────────────────────────────────────────│  ┌─┴──┐            ┌──┴───┐                               ┌──────┴──────┐      ┌─┴─┐  │User│            │Client│                               │Authorization│      │API│  └────┘            └──────┘                               └─────────────┘      └───┘ </pre>  </details>  With a `client_id`, you can use the authorization code flow. You first need to build an authorization URL.  ### Authorization  The authorization URL is: `http://10.254.10.7/readeck/authorize` and it receives the following query parameters:  | Name                    | Description                                                                  | | :---------------------- | :--------------------------------------------------------------------------- | | `client_id`             | OAuth Client ID                                                              | | `redirect_uri`          | Redirection URI (must match exactly one given during client registration)    | | `scope`                 | Space separated list of [scopes](#overview--available-scopes). At least one. | | `code_challenge`        | [PKCE](#overview--pkce) Challenge (mandatory)                                | | `code_challenge_method` | Only `S256` is allowed                                                       | | `state`                 | Optional [client state](#overview--state)                                    |  Sending a state is not mandatory but strongly advised to prevent cross site request forgery.  ### Authorization result  Once a user grants or denies an authorization request, it will be redirected to the `redirect_uri` with the following query parameters:  | Name    | Description                                                           | | :------ | :-------------------------------------------------------------------- | | `code`  | The authorization code that the client must pass to the token request | | `state` | The state as initially set by the client                              |  In case of error (request denied by the user or something else), the redirection contains the following query parameters:  | Name                | Description                                              | | :------------------ | :------------------------------------------------------- | | `error`             | Error code (can be `invalid_request` or `access_denied`) | | `error_description` | Error description                                        | | `state`             | The state as initially set by the client                 |  Once you receive a code, you can proceed to the [Token Request](#post-/oauth/token) to eventually receive an access token that will let you use the API.  ### PKCE  The authorization code flow requires that you use [PKCE](https://datatracker.ietf.org/doc/html/rfc7636) with an S256 method only (the \"plain\" method is not allowed).  1. The client creates a random **verifier** and produces a SHA-256 hash that is encoded in base64 to make a **challenge**. 2. The **challenge** is added to the authorization URL as `code_challenge` query parameter. 3. When requesting the token, the client sends the **verifier** as `code_verifier` parameter. Then the server, that kept track of the challenge can check it matches the received verifier.  **Important**: The challenge must be base64 encoded, **with URL encoding** and **without padding**.  <details part=\"details\"> <summary>Javascript example of a verifier and challenge generation</summary>  ```js // This generates a 64 character long random alphanumeric string. function generateRandomString() {   const alphabet =     \"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\"   let res = \"\"   const buf = new Uint8Array(64)   crypto.getRandomValues(buf)   for (let i in buf) {     res += alphabet[buf[i] % alphabet.length]   }   return res }  // This hashes the verifier and encodes the hash to URL safe base64. async function pkceChallengeFromVerifier(v) {   const b = await crypto.subtle.digest(\"SHA-256\", new TextEncoder().encode(v))   return btoa(String.fromCharCode(...new Uint8Array(b)))     .replaceAll(\"+\", \"-\")     .replaceAll(\"/\", \"_\")     .replaceAll(\"=\", \"\") }  const verifier = generateRandomString() pkceChallengeFromVerifier(verifier).then((challenge) => {   console.log(verifier)   console.log(challenge) }) ```  </details>  ### State  The `state` parameter that the client can add to the authorization URL is for the client only. When present, it is sent back in the redirection URI that contains the authorization code. The client can keep track of it and check it matches its initial value. It is strongly recommended to use it.  ## OAuth Device Code Flow  The Device Code Flow is used by browserless or input-constrained devices in the device flow to exchange a previously obtained device code for an access token. An e-reader is a good candidate for using this flow.  <details> <summary>Device Code Flow</summary> <pre role=\"img\" aria-label=\"Device Code sequence diagram\">  ┌────┐               ┌──────┐                         ┌─────────────┐  │User│               │Client│                         │Authorization│  └─┬──┘               └──┬───┘                         └──────┬──────┘    │                     │                                    │    │                     │(1) Request device code             │    │                     │───────────────────────────────────>│    │                     │                                    │    │                     │(2) Return device code, user code,  │    │                     │URL and interval                    │    │                     │<───────────────────────────────────│    │                     │                                    │    │(3) Provide user code│                                    │    │    and URL to user  │                                    │    │ <───────────────────│                                    │    │                   ┌────┐───────────────────────────────────┐    │                   │Loop│                                 │ │    │                   └────┘                                 │ │    │                   │ │                                    │ │    │                   │ │(4) Poll for authorization          │ │    │                   │ │───────────────────────────────────>│ │    │                   │ │                                    │ │    │                   │ │               authorization_pending│ │    │                   │ │<───────────────────────────────────│ │    │                   │ │                                    │ │    │                   └────────────────────────────────────────┘    │                     │                                    │    │(5) Open authorization URL and enter user code            │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │(5) Approve client access                                 │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │                     │             (6) Return access_token│    │                     │<───────────────────────────────────│    │                     │                                    │  ┌─┴──┐               ┌──┴───┐                         ┌──────┴──────┐  │User│               │Client│                         │Authorization│  └────┘               └──────┘                         └─────────────┘ </pre> </details>  1. The client request access from Readeck on the [Device Authorization route](#post-/oauth/device) 2. Readeck issues a device code, an end-user code and provides the end-user verification URI. This information is valid for 5 minutes. 3. The client instructs the user to visit the provided end-user verification URI. The client provides the user with the end-user code to enter in order to review the authorization request. 4. While the user reviews the client's request (step 5), the client repeatedly polls the [Token route](#post-/oauth/token) to find out if the user completed the user authorization step. The client includes the device code and its client identifier. The token route can only be polled every 5 seconds. 5. After authentication, Readeck prompts the user to input the user code provided by the device client and prompts the user to accept or decline the request. 6. Readeck validates the device code provided by the client and responds with the access token if the client is granted access, an error if they are denied access, or a pending state, indicating that the client should continue to poll.  <details> <summary>Python example of the device flow</summary>  ```python import json import time  import httpx   def main():     client = httpx.Client(         base_url=\"http://10.254.10.7/readeck\",         headers={\"Accept\": \"application/json\"},     )      # Create a client     rsp = client.post(         \"api/oauth/client\",         data={             \"client_name\": \"Test App\",             \"client_uri\": \"https://example.net/\",             \"software_id\": uuid.uuid4(),             \"software_version\": \"1.0.2\",             \"grant_types\": [\"urn:ietf:params:oauth:grant-type:device_code\"],         },     )     rsp.raise_for_status()     client_id = rsp.json()[\"client_id\"]      # Get user code.     rsp = client.post(         \"api/oauth/device\",         data={             \"client_id\": client_id,             \"scope\": \"bookmarks:read bookmarks:write\",         },     )     rsp.raise_for_status()      req_data = rsp.json()      # The client keeps the device code for itself.     device_code = req_data[\"device_code\"]      # User code with a separator for better readability     user_code = f\"{req_data['user_code'][0:4]}-{req_data['user_code'][4:]}\"      # Refresh interval     interval = req_data[\"interval\"]      # Information the client must provide the user with.     print(f\"CODE         : {user_code}\")     print(f\"URL          : {req_data['verification_uri']}\")     print(f\"COMPLETE URL : {req_data['verification_uri_complete']}\")      # Now, the client waits for the user to accept or deny     # the authorization request.     wait = 0     while True:         if wait > 0:             # wait before the request so we can use continue in the loop             time.sleep(wait)         else:             wait = interval          rsp = client.post(             \"api/oauth/token\",             data={                 \"grant_type\": \"urn:ietf:params:oauth:grant-type:device_code\",                 \"client_id\": client_id,                 \"device_code\": device_code,             },         )         if rsp.status_code >= 500:             rsp.raise_for_status()          data = rsp.json()          if data.get(\"access_token\"):             print(\"Token retrieved!\")             print(json.dumps(data, indent=2))             return          error = data.get(\"error\")         match error:             case \"access_denied\":                 # The user denied the request                 print(\"Access was denied\")                 return             case \"slow_down\":                 # Server asks to slow down, we'll sleep 5s                 continue             case \"authorization_pending\":                 # Still waiting                 print(\"Waiting for authorization...\")                 continue             case \"expired_token\":                 # The request has expired                 print(\"Request has expired\")                 return             case _:                 print(f\"Fatal error: {error}\")                 return   if __name__ == \"__main__\":     main() ```  </details>   

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import List, Optional
from typing_extensions import Annotated
from readeck_cli.infrastructure.readeck_client.models.bookmark_create import BookmarkCreate
from readeck_cli.infrastructure.readeck_client.models.bookmark_info import BookmarkInfo
from readeck_cli.infrastructure.readeck_client.models.bookmark_summary import BookmarkSummary
from readeck_cli.infrastructure.readeck_client.models.bookmark_update import BookmarkUpdate
from readeck_cli.infrastructure.readeck_client.models.bookmark_updated import BookmarkUpdated
from readeck_cli.infrastructure.readeck_client.models.message import Message

from readeck_cli.infrastructure.readeck_client.api_client import ApiClient, RequestSerialized
from readeck_cli.infrastructure.readeck_client.api_response import ApiResponse
from readeck_cli.infrastructure.readeck_client.rest import RESTResponseType


class BookmarksApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def bookmarks_get(
        self,
        limit: Annotated[Optional[StrictInt], Field(description="Number of items per page")] = None,
        offset: Annotated[Optional[StrictInt], Field(description="Pagination offset")] = None,
        sort: Annotated[Optional[List[StrictStr]], Field(description="Sorting parameters")] = None,
        seed: Annotated[Optional[Annotated[int, Field(le=999999, strict=True, ge=0)]], Field(description="Seed for random ordering. Only needed when using `?sort=random` ")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A full text search string")] = None,
        title: Annotated[Optional[StrictStr], Field(description="Bookmark title")] = None,
        author: Annotated[Optional[StrictStr], Field(description="Author's name")] = None,
        site: Annotated[Optional[StrictStr], Field(description="Bookmark site name or domain")] = None,
        lang: Annotated[Optional[StrictStr], Field(description="Bookmark language code")] = None,
        type: Annotated[Optional[List[StrictStr]], Field(description="Bookmark type")] = None,
        labels: Annotated[Optional[StrictStr], Field(description="One or several labels")] = None,
        is_loaded: Annotated[Optional[StrictBool], Field(description="Filter by loaded state")] = None,
        has_errors: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without errors")] = None,
        has_labels: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without labels")] = None,
        has_notes: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with a note and/or annotations")] = None,
        is_marked: Annotated[Optional[StrictBool], Field(description="Filter by marked (favorite) status")] = None,
        is_archived: Annotated[Optional[StrictBool], Field(description="Filter by archived status")] = None,
        range_start: Optional[StrictStr] = None,
        range_end: Optional[StrictStr] = None,
        read_status: Annotated[Optional[List[StrictStr]], Field(description="Read progress status")] = None,
        id: Annotated[Optional[StrictStr], Field(description="One or more bookmark ID")] = None,
        collection: Annotated[Optional[StrictStr], Field(description="A collection ID")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[BookmarkSummary]:
        """Bookmark List

        This route returns a paginated bookmark list. 

        :param limit: Number of items per page
        :type limit: int
        :param offset: Pagination offset
        :type offset: int
        :param sort: Sorting parameters
        :type sort: List[str]
        :param seed: Seed for random ordering. Only needed when using `?sort=random` 
        :type seed: int
        :param search: A full text search string
        :type search: str
        :param title: Bookmark title
        :type title: str
        :param author: Author's name
        :type author: str
        :param site: Bookmark site name or domain
        :type site: str
        :param lang: Bookmark language code
        :type lang: str
        :param type: Bookmark type
        :type type: List[str]
        :param labels: One or several labels
        :type labels: str
        :param is_loaded: Filter by loaded state
        :type is_loaded: bool
        :param has_errors: Filter bookmarks with or without errors
        :type has_errors: bool
        :param has_labels: Filter bookmarks with or without labels
        :type has_labels: bool
        :param has_notes: Filter bookmarks with a note and/or annotations
        :type has_notes: bool
        :param is_marked: Filter by marked (favorite) status
        :type is_marked: bool
        :param is_archived: Filter by archived status
        :type is_archived: bool
        :param range_start:
        :type range_start: str
        :param range_end:
        :type range_end: str
        :param read_status: Read progress status
        :type read_status: List[str]
        :param id: One or more bookmark ID
        :type id: str
        :param collection: A collection ID
        :type collection: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_get_serialize(
            limit=limit,
            offset=offset,
            sort=sort,
            seed=seed,
            search=search,
            title=title,
            author=author,
            site=site,
            lang=lang,
            type=type,
            labels=labels,
            is_loaded=is_loaded,
            has_errors=has_errors,
            has_labels=has_labels,
            has_notes=has_notes,
            is_marked=is_marked,
            is_archived=is_archived,
            range_start=range_start,
            range_end=range_end,
            read_status=read_status,
            id=id,
            collection=collection,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "List[BookmarkSummary]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def bookmarks_get_with_http_info(
        self,
        limit: Annotated[Optional[StrictInt], Field(description="Number of items per page")] = None,
        offset: Annotated[Optional[StrictInt], Field(description="Pagination offset")] = None,
        sort: Annotated[Optional[List[StrictStr]], Field(description="Sorting parameters")] = None,
        seed: Annotated[Optional[Annotated[int, Field(le=999999, strict=True, ge=0)]], Field(description="Seed for random ordering. Only needed when using `?sort=random` ")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A full text search string")] = None,
        title: Annotated[Optional[StrictStr], Field(description="Bookmark title")] = None,
        author: Annotated[Optional[StrictStr], Field(description="Author's name")] = None,
        site: Annotated[Optional[StrictStr], Field(description="Bookmark site name or domain")] = None,
        lang: Annotated[Optional[StrictStr], Field(description="Bookmark language code")] = None,
        type: Annotated[Optional[List[StrictStr]], Field(description="Bookmark type")] = None,
        labels: Annotated[Optional[StrictStr], Field(description="One or several labels")] = None,
        is_loaded: Annotated[Optional[StrictBool], Field(description="Filter by loaded state")] = None,
        has_errors: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without errors")] = None,
        has_labels: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without labels")] = None,
        has_notes: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with a note and/or annotations")] = None,
        is_marked: Annotated[Optional[StrictBool], Field(description="Filter by marked (favorite) status")] = None,
        is_archived: Annotated[Optional[StrictBool], Field(description="Filter by archived status")] = None,
        range_start: Optional[StrictStr] = None,
        range_end: Optional[StrictStr] = None,
        read_status: Annotated[Optional[List[StrictStr]], Field(description="Read progress status")] = None,
        id: Annotated[Optional[StrictStr], Field(description="One or more bookmark ID")] = None,
        collection: Annotated[Optional[StrictStr], Field(description="A collection ID")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[BookmarkSummary]]:
        """Bookmark List

        This route returns a paginated bookmark list. 

        :param limit: Number of items per page
        :type limit: int
        :param offset: Pagination offset
        :type offset: int
        :param sort: Sorting parameters
        :type sort: List[str]
        :param seed: Seed for random ordering. Only needed when using `?sort=random` 
        :type seed: int
        :param search: A full text search string
        :type search: str
        :param title: Bookmark title
        :type title: str
        :param author: Author's name
        :type author: str
        :param site: Bookmark site name or domain
        :type site: str
        :param lang: Bookmark language code
        :type lang: str
        :param type: Bookmark type
        :type type: List[str]
        :param labels: One or several labels
        :type labels: str
        :param is_loaded: Filter by loaded state
        :type is_loaded: bool
        :param has_errors: Filter bookmarks with or without errors
        :type has_errors: bool
        :param has_labels: Filter bookmarks with or without labels
        :type has_labels: bool
        :param has_notes: Filter bookmarks with a note and/or annotations
        :type has_notes: bool
        :param is_marked: Filter by marked (favorite) status
        :type is_marked: bool
        :param is_archived: Filter by archived status
        :type is_archived: bool
        :param range_start:
        :type range_start: str
        :param range_end:
        :type range_end: str
        :param read_status: Read progress status
        :type read_status: List[str]
        :param id: One or more bookmark ID
        :type id: str
        :param collection: A collection ID
        :type collection: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_get_serialize(
            limit=limit,
            offset=offset,
            sort=sort,
            seed=seed,
            search=search,
            title=title,
            author=author,
            site=site,
            lang=lang,
            type=type,
            labels=labels,
            is_loaded=is_loaded,
            has_errors=has_errors,
            has_labels=has_labels,
            has_notes=has_notes,
            is_marked=is_marked,
            is_archived=is_archived,
            range_start=range_start,
            range_end=range_end,
            read_status=read_status,
            id=id,
            collection=collection,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "List[BookmarkSummary]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def bookmarks_get_without_preload_content(
        self,
        limit: Annotated[Optional[StrictInt], Field(description="Number of items per page")] = None,
        offset: Annotated[Optional[StrictInt], Field(description="Pagination offset")] = None,
        sort: Annotated[Optional[List[StrictStr]], Field(description="Sorting parameters")] = None,
        seed: Annotated[Optional[Annotated[int, Field(le=999999, strict=True, ge=0)]], Field(description="Seed for random ordering. Only needed when using `?sort=random` ")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A full text search string")] = None,
        title: Annotated[Optional[StrictStr], Field(description="Bookmark title")] = None,
        author: Annotated[Optional[StrictStr], Field(description="Author's name")] = None,
        site: Annotated[Optional[StrictStr], Field(description="Bookmark site name or domain")] = None,
        lang: Annotated[Optional[StrictStr], Field(description="Bookmark language code")] = None,
        type: Annotated[Optional[List[StrictStr]], Field(description="Bookmark type")] = None,
        labels: Annotated[Optional[StrictStr], Field(description="One or several labels")] = None,
        is_loaded: Annotated[Optional[StrictBool], Field(description="Filter by loaded state")] = None,
        has_errors: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without errors")] = None,
        has_labels: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with or without labels")] = None,
        has_notes: Annotated[Optional[StrictBool], Field(description="Filter bookmarks with a note and/or annotations")] = None,
        is_marked: Annotated[Optional[StrictBool], Field(description="Filter by marked (favorite) status")] = None,
        is_archived: Annotated[Optional[StrictBool], Field(description="Filter by archived status")] = None,
        range_start: Optional[StrictStr] = None,
        range_end: Optional[StrictStr] = None,
        read_status: Annotated[Optional[List[StrictStr]], Field(description="Read progress status")] = None,
        id: Annotated[Optional[StrictStr], Field(description="One or more bookmark ID")] = None,
        collection: Annotated[Optional[StrictStr], Field(description="A collection ID")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Bookmark List

        This route returns a paginated bookmark list. 

        :param limit: Number of items per page
        :type limit: int
        :param offset: Pagination offset
        :type offset: int
        :param sort: Sorting parameters
        :type sort: List[str]
        :param seed: Seed for random ordering. Only needed when using `?sort=random` 
        :type seed: int
        :param search: A full text search string
        :type search: str
        :param title: Bookmark title
        :type title: str
        :param author: Author's name
        :type author: str
        :param site: Bookmark site name or domain
        :type site: str
        :param lang: Bookmark language code
        :type lang: str
        :param type: Bookmark type
        :type type: List[str]
        :param labels: One or several labels
        :type labels: str
        :param is_loaded: Filter by loaded state
        :type is_loaded: bool
        :param has_errors: Filter bookmarks with or without errors
        :type has_errors: bool
        :param has_labels: Filter bookmarks with or without labels
        :type has_labels: bool
        :param has_notes: Filter bookmarks with a note and/or annotations
        :type has_notes: bool
        :param is_marked: Filter by marked (favorite) status
        :type is_marked: bool
        :param is_archived: Filter by archived status
        :type is_archived: bool
        :param range_start:
        :type range_start: str
        :param range_end:
        :type range_end: str
        :param read_status: Read progress status
        :type read_status: List[str]
        :param id: One or more bookmark ID
        :type id: str
        :param collection: A collection ID
        :type collection: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_get_serialize(
            limit=limit,
            offset=offset,
            sort=sort,
            seed=seed,
            search=search,
            title=title,
            author=author,
            site=site,
            lang=lang,
            type=type,
            labels=labels,
            is_loaded=is_loaded,
            has_errors=has_errors,
            has_labels=has_labels,
            has_notes=has_notes,
            is_marked=is_marked,
            is_archived=is_archived,
            range_start=range_start,
            range_end=range_end,
            read_status=read_status,
            id=id,
            collection=collection,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "List[BookmarkSummary]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _bookmarks_get_serialize(
        self,
        limit,
        offset,
        sort,
        seed,
        search,
        title,
        author,
        site,
        lang,
        type,
        labels,
        is_loaded,
        has_errors,
        has_labels,
        has_notes,
        is_marked,
        is_archived,
        range_start,
        range_end,
        read_status,
        id,
        collection,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
            'sort': 'multi',
            'type': 'multi',
            'read_status': 'multi',
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if limit is not None:
            
            _query_params.append(('limit', limit))
            
        if offset is not None:
            
            _query_params.append(('offset', offset))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if seed is not None:
            
            _query_params.append(('seed', seed))
            
        if search is not None:
            
            _query_params.append(('search', search))
            
        if title is not None:
            
            _query_params.append(('title', title))
            
        if author is not None:
            
            _query_params.append(('author', author))
            
        if site is not None:
            
            _query_params.append(('site', site))
            
        if lang is not None:
            
            _query_params.append(('lang', lang))
            
        if type is not None:
            
            _query_params.append(('type', type))
            
        if labels is not None:
            
            _query_params.append(('labels', labels))
            
        if is_loaded is not None:
            
            _query_params.append(('is_loaded', is_loaded))
            
        if has_errors is not None:
            
            _query_params.append(('has_errors', has_errors))
            
        if has_labels is not None:
            
            _query_params.append(('has_labels', has_labels))
            
        if has_notes is not None:
            
            _query_params.append(('has_notes', has_notes))
            
        if is_marked is not None:
            
            _query_params.append(('is_marked', is_marked))
            
        if is_archived is not None:
            
            _query_params.append(('is_archived', is_archived))
            
        if range_start is not None:
            
            _query_params.append(('range_start', range_start))
            
        if range_end is not None:
            
            _query_params.append(('range_end', range_end))
            
        if read_status is not None:
            
            _query_params.append(('read_status', read_status))
            
        if id is not None:
            
            _query_params.append(('id', id))
            
        if collection is not None:
            
            _query_params.append(('collection', collection))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'bearer'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/bookmarks',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def bookmarks_id_delete(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Bookmark Delete

        Deletes a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_delete_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '204': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def bookmarks_id_delete_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Bookmark Delete

        Deletes a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_delete_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '204': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def bookmarks_id_delete_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Bookmark Delete

        Deletes a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_delete_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '204': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _bookmarks_id_delete_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'bearer'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/bookmarks/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def bookmarks_id_get(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> BookmarkInfo:
        """Bookmark Details

        Retrieves a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_get_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '200': "BookmarkInfo",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def bookmarks_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[BookmarkInfo]:
        """Bookmark Details

        Retrieves a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_get_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '200': "BookmarkInfo",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def bookmarks_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Bookmark Details

        Retrieves a saved bookmark

        :param id: Bookmark ID (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_get_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '200': "BookmarkInfo",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _bookmarks_id_get_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'bearer'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/bookmarks/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def bookmarks_id_patch(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        bookmark_update: Optional[BookmarkUpdate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> BookmarkUpdated:
        """Bookmark Update

        This route updates some bookmark's properties. Every input value is optional. Upon success, it returns a mapping of changed values. 

        :param id: Bookmark ID (required)
        :type id: str
        :param bookmark_update:
        :type bookmark_update: BookmarkUpdate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_patch_serialize(
            id=id,
            bookmark_update=bookmark_update,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "BookmarkUpdated",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def bookmarks_id_patch_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        bookmark_update: Optional[BookmarkUpdate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[BookmarkUpdated]:
        """Bookmark Update

        This route updates some bookmark's properties. Every input value is optional. Upon success, it returns a mapping of changed values. 

        :param id: Bookmark ID (required)
        :type id: str
        :param bookmark_update:
        :type bookmark_update: BookmarkUpdate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_patch_serialize(
            id=id,
            bookmark_update=bookmark_update,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "BookmarkUpdated",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def bookmarks_id_patch_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="Bookmark ID")],
        bookmark_update: Optional[BookmarkUpdate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Bookmark Update

        This route updates some bookmark's properties. Every input value is optional. Upon success, it returns a mapping of changed values. 

        :param id: Bookmark ID (required)
        :type id: str
        :param bookmark_update:
        :type bookmark_update: BookmarkUpdate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_id_patch_serialize(
            id=id,
            bookmark_update=bookmark_update,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '200': "BookmarkUpdated",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _bookmarks_id_patch_serialize(
        self,
        id,
        bookmark_update,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if bookmark_update is not None:
            _body_params = bookmark_update


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'bearer'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/bookmarks/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def bookmarks_post(
        self,
        bookmark_create: Optional[BookmarkCreate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> Message:
        """Bookmark Create

         This route creates a new bookmark.  Only the `url` parameter is mandatory. The route's body can be a JSON object or a `multipart/form-data` payload.  ### Sending an existing HTML content as a page  If you want to save a page for which you already have an HTML content, you can call this route with an `html` parameter that contains the page's source. This parameter is accepted in `multipart/form-data` and `JSON`.  #### Example with a JSON payload  ```http POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: application/json Accept: application/json  {     \"url\": \"https://example.org/\",     \"html\": \"<p>test\" } ```  #### Example with a multipart payload  ```request POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"html\"; filename=\"_\"  <p>test --delimiter123-- ```  ### Sending non HTML and/or multiple resources  If you want to save a page with extra resources (such as images), you need to call this route with a `multipart/form-data` body and some `resource` values.  Each `resource` entry is a file part, it **must** contain the following headers:  | Name                  | Content                                    | | :-------------------- | :----------------------------------------- | | `Content-Disposition` | `form-data; name=\"resource\"; filename=\"_\"` | | `Location`            | `https://some-url`                         |  The `filename` property in `Content-Disposition` **must** have a value, otherwise headers won't be read properly. The value doesn't matter and can be, for example, `_`.  A resource can have more headers, like a `Content-Type`.  #### Example  ``` POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/ Content-Type: text/html  <p>test     <img src=\"/logo.svg\"> --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/logo.svg Content-Type: image/svg+xml  <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1 1\"> <path d=\"M0,0h1v1H0\" fill=\"#f00\"/> </svg> --delimiter123-- ```   

        :param bookmark_create:
        :type bookmark_create: BookmarkCreate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_post_serialize(
            bookmark_create=bookmark_create,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '202': "Message",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def bookmarks_post_with_http_info(
        self,
        bookmark_create: Optional[BookmarkCreate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[Message]:
        """Bookmark Create

         This route creates a new bookmark.  Only the `url` parameter is mandatory. The route's body can be a JSON object or a `multipart/form-data` payload.  ### Sending an existing HTML content as a page  If you want to save a page for which you already have an HTML content, you can call this route with an `html` parameter that contains the page's source. This parameter is accepted in `multipart/form-data` and `JSON`.  #### Example with a JSON payload  ```http POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: application/json Accept: application/json  {     \"url\": \"https://example.org/\",     \"html\": \"<p>test\" } ```  #### Example with a multipart payload  ```request POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"html\"; filename=\"_\"  <p>test --delimiter123-- ```  ### Sending non HTML and/or multiple resources  If you want to save a page with extra resources (such as images), you need to call this route with a `multipart/form-data` body and some `resource` values.  Each `resource` entry is a file part, it **must** contain the following headers:  | Name                  | Content                                    | | :-------------------- | :----------------------------------------- | | `Content-Disposition` | `form-data; name=\"resource\"; filename=\"_\"` | | `Location`            | `https://some-url`                         |  The `filename` property in `Content-Disposition` **must** have a value, otherwise headers won't be read properly. The value doesn't matter and can be, for example, `_`.  A resource can have more headers, like a `Content-Type`.  #### Example  ``` POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/ Content-Type: text/html  <p>test     <img src=\"/logo.svg\"> --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/logo.svg Content-Type: image/svg+xml  <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1 1\"> <path d=\"M0,0h1v1H0\" fill=\"#f00\"/> </svg> --delimiter123-- ```   

        :param bookmark_create:
        :type bookmark_create: BookmarkCreate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_post_serialize(
            bookmark_create=bookmark_create,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '202': "Message",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def bookmarks_post_without_preload_content(
        self,
        bookmark_create: Optional[BookmarkCreate] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Bookmark Create

         This route creates a new bookmark.  Only the `url` parameter is mandatory. The route's body can be a JSON object or a `multipart/form-data` payload.  ### Sending an existing HTML content as a page  If you want to save a page for which you already have an HTML content, you can call this route with an `html` parameter that contains the page's source. This parameter is accepted in `multipart/form-data` and `JSON`.  #### Example with a JSON payload  ```http POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: application/json Accept: application/json  {     \"url\": \"https://example.org/\",     \"html\": \"<p>test\" } ```  #### Example with a multipart payload  ```request POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"html\"; filename=\"_\"  <p>test --delimiter123-- ```  ### Sending non HTML and/or multiple resources  If you want to save a page with extra resources (such as images), you need to call this route with a `multipart/form-data` body and some `resource` values.  Each `resource` entry is a file part, it **must** contain the following headers:  | Name                  | Content                                    | | :-------------------- | :----------------------------------------- | | `Content-Disposition` | `form-data; name=\"resource\"; filename=\"_\"` | | `Location`            | `https://some-url`                         |  The `filename` property in `Content-Disposition` **must** have a value, otherwise headers won't be read properly. The value doesn't matter and can be, for example, `_`.  A resource can have more headers, like a `Content-Type`.  #### Example  ``` POST http://10.254.10.7/readeck/api/bookmarks  Content-Type: multipart/form-data;boundary=\"delimiter123\" Accept: application/json  --delimiter123 Content-Disposition: form-data; name=\"url\"  https://example.org/ --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/ Content-Type: text/html  <p>test     <img src=\"/logo.svg\"> --delimiter123 Content-Disposition: form-data; name=\"resource\"; filename=\"_\" Location: https://example.org/logo.svg Content-Type: image/svg+xml  <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1 1\"> <path d=\"M0,0h1v1H0\" fill=\"#f00\"/> </svg> --delimiter123-- ```   

        :param bookmark_create:
        :type bookmark_create: BookmarkCreate
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._bookmarks_post_serialize(
            bookmark_create=bookmark_create,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '401': "Message",
            '403': "Message",
            '422': "BookmarksGet422Response",
            '202': "Message",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _bookmarks_post_serialize(
        self,
        bookmark_create,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if bookmark_create is not None:
            _body_params = bookmark_create


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'bearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/bookmarks',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


