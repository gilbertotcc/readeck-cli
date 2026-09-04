"""
    Readeck API

    # Introduction  The Readeck API provides REST endpoints that can be used for any purpose, should it be a mobile application, a script, you name it.  ## API Endpoint  You can access this API on `http://10.254.10.7/readeck/api`.  Most of your requests and responses are using JSON as the exchange format.  ## Test the API  On this documentation, you can test every route.  If you don't provide an API token in [Authentication](#auth), you can still test all the routes but note that the given curl examples only work with an API token.  # Token Authentication  If you're writing a script for yourself, the easiest way is to [generate an API token](../profile/tokens) that you can use using the `Bearer` HTTP authorization scheme.  For example, you first request will look like:  ```sh curl -H \"Authorization: Bearer <TOKEN>\" http://10.254.10.7/readeck/api/profile ```  Or, in NodeJS:  ```js fetch(\"http://10.254.10.7/readeck/api/profile\", {     headers: {     \"Authorization\": \"Bearer <TOKEN>\",     }, }) ```   # Authentication with OAuth  If you're writing an application that requires a user to grant the application permission to access their Readeck instance, you should not ask a user to create an API Token but instead, implement the necessary OAuth flow so that your application can retrieve a token in a user friendly way.  ## Available Scopes  An OAuth token grants the application some permissions based on the requested scopes. This are the available scopes you can request:  | Name              | Description                    | | :---------------- | ------------------------------ | | `bookmarks:read`  | Read only access to bookmarks  | | `bookmarks:write` | Write only access to bookmarks | | `profile:read`    | Extended profile information   |  You can see which scope applies on each route of this documentation. A route without a scope (and not \"public\") is not available with an OAuth token.  ## Client Registration  Before you can start the authorization flow, you first need to register a client on the Readeck instance.  <details> <summary>Client Registration Flow</summary> <pre role=\"img\" aria-label=\"Client Registration sequence diagram\">  ┌──────┐                 ┌────────────┐  │Client│                 │Registration│  └──┬───┘                 └─────┬──────┘     │                           │     │Client Registration Request│     │POST /api/oauth/client     │     │──────────────────────────>│     │                           │     │Client Information Response│     │<──────────────────────────│  ┌──┴───┐                 ┌─────┴──────┐  │Client│                 │Registration│  └──────┘                 └────────────┘ </pre> </details>  Readeck implement [OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591). You can register a client by querying the [Client Creation Route](#post-/oauth/client).  Upon registration, you'll receive a `client_id` that you can use in the next authorization step.  Unlike more traditional client implementations, Readeck OAuth clients are ephemeral:  - You **must** register a new client each time you start an authorization flow. - The Client is valid for 10 minutes after creation.  ## OAuth Authorization Code Flow  The Authorization Code Flow is used by clients to exchange an authorization code for an access token.  After the user returns to the client via the redirect URL, the application will get the authorization code from the URL and use it to request an access token.  This flow can only be used when, on the same device, the client can:  - send the user to the authorization page - process the redirect URL to retrieve the authorization code  On a device without a browser, a client can use the [Device Code Flow](#overview--oauth-device-code-flow).  <details> <summary>Authorization Code Flow</summary>  <pre role=\"img\" aria-label=\"Authorization Code sequence diagram\">  ┌────┐            ┌──────┐                               ┌─────────────┐      ┌───┐  │User│            │Client│                               │Authorization│      │API│  └─┬──┘            └──┬───┘                               └──────┬──────┘      └─┬─┘    │                  │                                          │               │    │Enter instance URL│                                          │               │    │─────────────────>│                                          │               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Generate PKCE verifier and challenge  │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │        Open Authorization URL            │               │    │                  │        GET /authorize?...                │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │         Redirect to login/authorization prompt              │               │    │<────────────────────────────────────────────────────────────│               │    │                  │                                          │               │    │Authorize Client                                             │               │    │POST /authorize?...                                          │               │    │────────────────────────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │          Authorization Code              │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Check state                           │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │Request Token (with code and verifier)    │               │    │                  │POST /api/oauth/token                     │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │                                          │──┐            │    │                  │                                          │  │ Check PKCE │    │                  │                                          │<─┘            │    │                  │                                          │               │    │                  │             Access Token                 │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │         Request data with Access Token   │               │    │                  │─────────────────────────────────────────────────────────>│    │                  │                                          │               │    │                  │                    Response              │               │    │                  │<─────────────────────────────────────────────────────────│  ┌─┴──┐            ┌──┴───┐                               ┌──────┴──────┐      ┌─┴─┐  │User│            │Client│                               │Authorization│      │API│  └────┘            └──────┘                               └─────────────┘      └───┘ </pre>  </details>  With a `client_id`, you can use the authorization code flow. You first need to build an authorization URL.  ### Authorization  The authorization URL is: `http://10.254.10.7/readeck/authorize` and it receives the following query parameters:  | Name                    | Description                                                                  | | :---------------------- | :--------------------------------------------------------------------------- | | `client_id`             | OAuth Client ID                                                              | | `redirect_uri`          | Redirection URI (must match exactly one given during client registration)    | | `scope`                 | Space separated list of [scopes](#overview--available-scopes). At least one. | | `code_challenge`        | [PKCE](#overview--pkce) Challenge (mandatory)                                | | `code_challenge_method` | Only `S256` is allowed                                                       | | `state`                 | Optional [client state](#overview--state)                                    |  Sending a state is not mandatory but strongly advised to prevent cross site request forgery.  ### Authorization result  Once a user grants or denies an authorization request, it will be redirected to the `redirect_uri` with the following query parameters:  | Name    | Description                                                           | | :------ | :-------------------------------------------------------------------- | | `code`  | The authorization code that the client must pass to the token request | | `state` | The state as initially set by the client                              |  In case of error (request denied by the user or something else), the redirection contains the following query parameters:  | Name                | Description                                              | | :------------------ | :------------------------------------------------------- | | `error`             | Error code (can be `invalid_request` or `access_denied`) | | `error_description` | Error description                                        | | `state`             | The state as initially set by the client                 |  Once you receive a code, you can proceed to the [Token Request](#post-/oauth/token) to eventually receive an access token that will let you use the API.  ### PKCE  The authorization code flow requires that you use [PKCE](https://datatracker.ietf.org/doc/html/rfc7636) with an S256 method only (the \"plain\" method is not allowed).  1. The client creates a random **verifier** and produces a SHA-256 hash that is encoded in base64 to make a **challenge**. 2. The **challenge** is added to the authorization URL as `code_challenge` query parameter. 3. When requesting the token, the client sends the **verifier** as `code_verifier` parameter. Then the server, that kept track of the challenge can check it matches the received verifier.  **Important**: The challenge must be base64 encoded, **with URL encoding** and **without padding**.  <details part=\"details\"> <summary>Javascript example of a verifier and challenge generation</summary>  ```js // This generates a 64 character long random alphanumeric string. function generateRandomString() {   const alphabet =     \"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\"   let res = \"\"   const buf = new Uint8Array(64)   crypto.getRandomValues(buf)   for (let i in buf) {     res += alphabet[buf[i] % alphabet.length]   }   return res }  // This hashes the verifier and encodes the hash to URL safe base64. async function pkceChallengeFromVerifier(v) {   const b = await crypto.subtle.digest(\"SHA-256\", new TextEncoder().encode(v))   return btoa(String.fromCharCode(...new Uint8Array(b)))     .replaceAll(\"+\", \"-\")     .replaceAll(\"/\", \"_\")     .replaceAll(\"=\", \"\") }  const verifier = generateRandomString() pkceChallengeFromVerifier(verifier).then((challenge) => {   console.log(verifier)   console.log(challenge) }) ```  </details>  ### State  The `state` parameter that the client can add to the authorization URL is for the client only. When present, it is sent back in the redirection URI that contains the authorization code. The client can keep track of it and check it matches its initial value. It is strongly recommended to use it.  ## OAuth Device Code Flow  The Device Code Flow is used by browserless or input-constrained devices in the device flow to exchange a previously obtained device code for an access token. An e-reader is a good candidate for using this flow.  <details> <summary>Device Code Flow</summary> <pre role=\"img\" aria-label=\"Device Code sequence diagram\">  ┌────┐               ┌──────┐                         ┌─────────────┐  │User│               │Client│                         │Authorization│  └─┬──┘               └──┬───┘                         └──────┬──────┘    │                     │                                    │    │                     │(1) Request device code             │    │                     │───────────────────────────────────>│    │                     │                                    │    │                     │(2) Return device code, user code,  │    │                     │URL and interval                    │    │                     │<───────────────────────────────────│    │                     │                                    │    │(3) Provide user code│                                    │    │    and URL to user  │                                    │    │ <───────────────────│                                    │    │                   ┌────┐───────────────────────────────────┐    │                   │Loop│                                 │ │    │                   └────┘                                 │ │    │                   │ │                                    │ │    │                   │ │(4) Poll for authorization          │ │    │                   │ │───────────────────────────────────>│ │    │                   │ │                                    │ │    │                   │ │               authorization_pending│ │    │                   │ │<───────────────────────────────────│ │    │                   │ │                                    │ │    │                   └────────────────────────────────────────┘    │                     │                                    │    │(5) Open authorization URL and enter user code            │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │(5) Approve client access                                 │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │                     │             (6) Return access_token│    │                     │<───────────────────────────────────│    │                     │                                    │  ┌─┴──┐               ┌──┴───┐                         ┌──────┴──────┐  │User│               │Client│                         │Authorization│  └────┘               └──────┘                         └─────────────┘ </pre> </details>  1. The client request access from Readeck on the [Device Authorization route](#post-/oauth/device) 2. Readeck issues a device code, an end-user code and provides the end-user verification URI. This information is valid for 5 minutes. 3. The client instructs the user to visit the provided end-user verification URI. The client provides the user with the end-user code to enter in order to review the authorization request. 4. While the user reviews the client's request (step 5), the client repeatedly polls the [Token route](#post-/oauth/token) to find out if the user completed the user authorization step. The client includes the device code and its client identifier. The token route can only be polled every 5 seconds. 5. After authentication, Readeck prompts the user to input the user code provided by the device client and prompts the user to accept or decline the request. 6. Readeck validates the device code provided by the client and responds with the access token if the client is granted access, an error if they are denied access, or a pending state, indicating that the client should continue to poll.  <details> <summary>Python example of the device flow</summary>  ```python import json import time  import httpx   def main():     client = httpx.Client(         base_url=\"http://10.254.10.7/readeck\",         headers={\"Accept\": \"application/json\"},     )      # Create a client     rsp = client.post(         \"api/oauth/client\",         data={             \"client_name\": \"Test App\",             \"client_uri\": \"https://example.net/\",             \"software_id\": uuid.uuid4(),             \"software_version\": \"1.0.2\",             \"grant_types\": [\"urn:ietf:params:oauth:grant-type:device_code\"],         },     )     rsp.raise_for_status()     client_id = rsp.json()[\"client_id\"]      # Get user code.     rsp = client.post(         \"api/oauth/device\",         data={             \"client_id\": client_id,             \"scope\": \"bookmarks:read bookmarks:write\",         },     )     rsp.raise_for_status()      req_data = rsp.json()      # The client keeps the device code for itself.     device_code = req_data[\"device_code\"]      # User code with a separator for better readability     user_code = f\"{req_data['user_code'][0:4]}-{req_data['user_code'][4:]}\"      # Refresh interval     interval = req_data[\"interval\"]      # Information the client must provide the user with.     print(f\"CODE         : {user_code}\")     print(f\"URL          : {req_data['verification_uri']}\")     print(f\"COMPLETE URL : {req_data['verification_uri_complete']}\")      # Now, the client waits for the user to accept or deny     # the authorization request.     wait = 0     while True:         if wait > 0:             # wait before the request so we can use continue in the loop             time.sleep(wait)         else:             wait = interval          rsp = client.post(             \"api/oauth/token\",             data={                 \"grant_type\": \"urn:ietf:params:oauth:grant-type:device_code\",                 \"client_id\": client_id,                 \"device_code\": device_code,             },         )         if rsp.status_code >= 500:             rsp.raise_for_status()          data = rsp.json()          if data.get(\"access_token\"):             print(\"Token retrieved!\")             print(json.dumps(data, indent=2))             return          error = data.get(\"error\")         match error:             case \"access_denied\":                 # The user denied the request                 print(\"Access was denied\")                 return             case \"slow_down\":                 # Server asks to slow down, we'll sleep 5s                 continue             case \"authorization_pending\":                 # Still waiting                 print(\"Waiting for authorization...\")                 continue             case \"expired_token\":                 # The request has expired                 print(\"Request has expired\")                 return             case _:                 print(f\"Fatal error: {error}\")                 return   if __name__ == \"__main__\":     main() ```  </details>   

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import copy
import http.client as httplib
import logging
from logging import FileHandler
import multiprocessing
import ssl
import sys
from typing import Any, ClassVar, Dict, List, Literal, Optional, TypedDict, Union
from urllib.parse import urlparse
from urllib.request import getproxies
from typing_extensions import NotRequired, Self

import urllib3


JSON_SCHEMA_VALIDATION_KEYWORDS = {
    'multipleOf', 'maximum', 'exclusiveMaximum',
    'minimum', 'exclusiveMinimum', 'maxLength',
    'minLength', 'pattern', 'maxItems', 'minItems'
}

ServerVariablesT = Dict[str, str]

GenericAuthSetting = TypedDict(
    "GenericAuthSetting",
    {
        "type": str,
        "in": str,
        "key": str,
        "value": str,
    },
)


OAuth2AuthSetting = TypedDict(
    "OAuth2AuthSetting",
    {
        "type": Literal["oauth2"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": str,
    },
)


APIKeyAuthSetting = TypedDict(
    "APIKeyAuthSetting",
    {
        "type": Literal["api_key"],
        "in": str,
        "key": str,
        "value": Optional[str],
    },
)


BasicAuthSetting = TypedDict(
    "BasicAuthSetting",
    {
        "type": Literal["basic"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": Optional[str],
    },
)


BearerFormatAuthSetting = TypedDict(
    "BearerFormatAuthSetting",
    {
        "type": Literal["bearer"],
        "in": Literal["header"],
        "format": Literal["JWT"],
        "key": Literal["Authorization"],
        "value": str,
    },
)


BearerAuthSetting = TypedDict(
    "BearerAuthSetting",
    {
        "type": Literal["bearer"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": str,
    },
)


HTTPSignatureAuthSetting = TypedDict(
    "HTTPSignatureAuthSetting",
    {
        "type": Literal["http-signature"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": None,
    },
)


AuthSettings = TypedDict(
    "AuthSettings",
    {
        "bearer": BearerAuthSetting,
    },
    total=False,
)


class HostSettingVariable(TypedDict):
    description: str
    default_value: str
    enum_values: List[str]


class HostSetting(TypedDict):
    url: str
    description: str
    variables: NotRequired[Dict[str, HostSettingVariable]]


class Configuration:
    """This class contains various settings of the API client.

    :param host: Base url.
    :param ignore_operation_servers
      Boolean to ignore operation servers for the API client.
      Config will use `host` as the base url regardless of the operation servers.
    :param api_key: Dict to store API key(s).
      Each entry in the dict specifies an API key.
      The dict key is the name of the security scheme in the OAS specification.
      The dict value is the API key secret.
    :param api_key_prefix: Dict to store API prefix (e.g. Bearer).
      The dict key is the name of the security scheme in the OAS specification.
      The dict value is an API key prefix when generating the auth data.
    :param username: Username for HTTP basic authentication.
    :param password: Password for HTTP basic authentication.
    :param access_token: Access token.
    :param server_index: Index to servers configuration.
    :param server_variables: Mapping with string values to replace variables in
      templated server configuration. The validation of enums is performed for
      variables with defined enum values before.
    :param server_operation_index: Mapping from operation ID to an index to server
      configuration.
    :param server_operation_variables: Mapping from operation ID to a mapping with
      string values to replace variables in templated server configuration.
      The validation of enums is performed for variables with defined enum
      values before.
    :param verify_ssl: bool - Set this to false to skip verifying SSL certificate
      when calling API from https server.
    :param ssl_ca_cert: str - the path to a file of concatenated CA certificates
      in PEM format.
    :param retries: int | urllib3.util.retry.Retry - Retry configuration.
    :param ca_cert_data: verify the peer using concatenated CA certificate data
      in PEM (str) or DER (bytes) format.
    :param cert_file: the path to a client certificate file, for mTLS.
    :param key_file: the path to a client key file, for mTLS.
    :param assert_hostname: Set this to True/False to enable/disable SSL hostname verification.
    :param tls_server_name: SSL/TLS Server Name Indication (SNI). Set this to the SNI value expected by the server.
    :param connection_pool_maxsize: Connection pool max size. None in the constructor is coerced to 100 for async and cpu_count * 5 for sync.
    :param proxy: Proxy URL.
    :param no_proxy: Comma-separated hosts that bypass the proxy.
    :param proxy_headers: Proxy headers.
    :param proxy_ssl_context: SSL context used only for the TLS handshake with the proxy itself, independent of the destination TLS settings.
    :param safe_chars_for_path_param: Safe characters for path parameter encoding.
    :param client_side_validation: Enable client-side validation. Default True.
    :param socket_options: Options to pass down to the underlying urllib3 socket.
    :param datetime_format: Datetime format string for serialization.
    :param date_format: Date format string for serialization.

    :Example:
    """

    _default: ClassVar[Optional[Self]] = None

    def __init__(
        self,
        host: Optional[str]=None,
        api_key: Optional[Dict[str, str]]=None,
        api_key_prefix: Optional[Dict[str, str]]=None,
        username: Optional[str]=None,
        password: Optional[str]=None,
        access_token: Optional[str]=None,
        server_index: Optional[int]=None,
        server_variables: Optional[ServerVariablesT]=None,
        server_operation_index: Optional[Dict[int, int]]=None,
        server_operation_variables: Optional[Dict[int, ServerVariablesT]]=None,
        ignore_operation_servers: bool=False,
        ssl_ca_cert: Optional[str]=None,
        retries: Optional[Union[int, urllib3.util.retry.Retry]] = None,
        ca_cert_data: Optional[Union[str, bytes]] = None,
        cert_file: Optional[str]=None,
        key_file: Optional[str]=None,
        verify_ssl: bool=True,
        assert_hostname: Optional[bool]=None,
        tls_server_name: Optional[str]=None,
        connection_pool_maxsize: Optional[int]=None,
        proxy: Optional[str]=None,
        no_proxy: Optional[str]=None,
        proxy_headers: Optional[Any]=None,
        proxy_ssl_context: Optional[ssl.SSLContext]=None,
        safe_chars_for_path_param: str='',
        client_side_validation: bool=True,
        socket_options: Optional[Any]=None,
        datetime_format: str="%Y-%m-%dT%H:%M:%S.%f%z",
        date_format: str="%Y-%m-%d",
        *,
        debug: Optional[bool] = None,
    ) -> None:
        """Constructor
        """
        self._base_path = "http://10.254.10.7/readeck/api" if host is None else host
        """Default Base url
        """
        self.server_index = 0 if server_index is None and host is None else server_index
        self.server_operation_index = server_operation_index or {}
        """Default server index
        """
        self.server_variables = server_variables or {}
        self.server_operation_variables = server_operation_variables or {}
        """Default server variables
        """
        self.ignore_operation_servers = ignore_operation_servers
        """Ignore operation servers
        """
        self.temp_folder_path = None
        """Temp file folder for downloading files
        """
        # Authentication Settings
        self.api_key = {}
        if api_key:
            self.api_key = api_key
        """dict to store API key(s)
        """
        self.api_key_prefix = {}
        if api_key_prefix:
            self.api_key_prefix = api_key_prefix
        """dict to store API prefix (e.g. Bearer)
        """
        self.refresh_api_key_hook = None
        """function hook to refresh API key if expired
        """
        self.username = username
        """Username for HTTP basic authentication
        """
        self.password = password
        """Password for HTTP basic authentication
        """
        self.access_token = access_token
        """Access token
        """
        self.logger = {}
        """Logging Settings
        """
        self.logger["package_logger"] = logging.getLogger("readeck_cli.infrastructure.readeck_client")
        self.logger["urllib3_logger"] = logging.getLogger("urllib3")
        self.logger_format = '%(asctime)s %(levelname)s %(message)s'
        """Log format
        """
        self.logger_stream_handler = None
        """Log stream handler
        """
        self.logger_file_handler: Optional[FileHandler] = None
        """Log file handler
        """
        self.logger_file = None
        """Debug file location
        """
        if debug is not None:
            self.debug = debug
        else:
            self.__debug = False
        """Debug switch
        """

        self.verify_ssl = verify_ssl
        """SSL/TLS verification
           Set this to false to skip verifying SSL certificate when calling API
           from https server.
        """
        self.ssl_ca_cert = ssl_ca_cert
        """Set this to customize the certificate file to verify the peer.
        """
        self.ca_cert_data = ca_cert_data
        """Set this to verify the peer using PEM (str) or DER (bytes)
           certificate data.
        """
        self.cert_file = cert_file
        """client certificate file
        """
        self.key_file = key_file
        """client key file
        """
        self.assert_hostname = assert_hostname
        """Set this to True/False to enable/disable SSL hostname verification.
        """
        self.tls_server_name = tls_server_name
        """SSL/TLS Server Name Indication (SNI)
           Set this to the SNI value expected by the server.
        """

        self.connection_pool_maxsize = connection_pool_maxsize if connection_pool_maxsize is not None else multiprocessing.cpu_count() * 5
        """urllib3 connection pool's maximum number of connections saved
           per pool. None in the constructor is coerced to cpu_count * 5.
        """

        # urllib3 does not read proxy environment variables itself:
        # https://github.com/urllib3/urllib3/issues/1785
        # A proxy taken from the environment is re-resolved when the host is
        # assigned; see the host setter.
        self._proxy_from_env = proxy is None
        if proxy is None or no_proxy is None:
            proxies = getproxies()
            if proxy is None:
                proxy = self._env_proxy(proxies, self.host)
            if no_proxy is None:
                no_proxy = proxies.get("no")
        self._proxy = proxy
        self.no_proxy = no_proxy
        """Hosts that bypass the proxy
        """
        self.proxy_headers = proxy_headers
        """Proxy headers
        """
        self.proxy_ssl_context = proxy_ssl_context
        """SSL context used only for the TLS handshake with the proxy itself
        (e.g. an HTTPS CONNECT tunnel), independent of the destination TLS
        settings above.
        """
        self.safe_chars_for_path_param = safe_chars_for_path_param
        """Safe chars for path_param
        """
        self.retries = retries
        """Retry configuration
        """
        # Enable client side validation
        self.client_side_validation = client_side_validation

        self.socket_options = socket_options
        """Options to pass down to the underlying urllib3 socket
        """

        self.datetime_format = datetime_format
        """datetime format
        """

        self.date_format = date_format
        """date format
        """

    def __deepcopy__(self, memo:  Dict[int, Any]) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == 'proxy_ssl_context':
                # ssl.SSLContext holds unpicklable C state and can't be deepcopied.
                setattr(result, k, v)
                continue
            if k not in ('logger', 'logger_file_handler'):
                setattr(result, k, copy.deepcopy(v, memo))
        # shallow copy of loggers
        result.logger = copy.copy(self.logger)
        # use setter to re-create the file handler (excluded from __dict__ copy)
        result.logger_file = self.logger_file

        return result

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

    @classmethod
    def set_default(cls, default: Optional[Self]) -> None:
        """Set default instance of configuration.

        It stores default configuration, which can be
        returned by get_default_copy method.

        :param default: object of Configuration
        """
        cls._default = default

    @classmethod
    def get_default_copy(cls) -> Self:
        """Deprecated. Please use `get_default` instead.

        Deprecated. Please use `get_default` instead.

        :return: The configuration object.
        """
        return cls.get_default()

    @classmethod
    def get_default(cls) -> Self:
        """Return the default configuration.

        This method returns newly created, based on default constructor,
        object of Configuration class or returns a copy of default
        configuration.

        :return: The configuration object.
        """
        if cls._default is None:
            cls._default = cls()
        return cls._default

    @property
    def logger_file(self) -> Optional[str]:
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :param value: The logger_file path.
        :type: str
        """
        return self.__logger_file

    @logger_file.setter
    def logger_file(self, value: Optional[str]) -> None:
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :param value: The logger_file path.
        :type: str
        """
        self.__logger_file = value
        if self.__logger_file:
            # If set logging file,
            # then add file handler and remove stream handler.
            self.logger_file_handler = logging.FileHandler(self.__logger_file)
            self.logger_file_handler.setFormatter(self.logger_formatter)
            for _, logger in self.logger.items():
                logger.addHandler(self.logger_file_handler)

    @property
    def debug(self) -> bool:
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        return self.__debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        self.__debug = value
        if self.__debug:
            # if debug status is True, turn on debug logging
            for _, logger in self.logger.items():
                logger.setLevel(logging.DEBUG)
            # turn on httplib debug
            httplib.HTTPConnection.debuglevel = 1
        else:
            # if debug status is False, turn off debug logging,
            # setting log level to default `logging.WARNING`
            for _, logger in self.logger.items():
                logger.setLevel(logging.WARNING)
            # turn off httplib debug
            httplib.HTTPConnection.debuglevel = 0

    @property
    def logger_format(self) -> str:
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        return self.__logger_format

    @logger_format.setter
    def logger_format(self, value: str) -> None:
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        self.__logger_format = value
        self.logger_formatter = logging.Formatter(self.__logger_format)

    def get_api_key_with_prefix(self, identifier: str, alias: Optional[str]=None) -> Optional[str]:
        """Gets API key (with prefix if set).

        :param identifier: The identifier of apiKey.
        :param alias: The alternative identifier of apiKey.
        :return: The token for api key authentication.
        """
        if self.refresh_api_key_hook is not None:
            self.refresh_api_key_hook(self)
        key = self.api_key.get(identifier, self.api_key.get(alias) if alias is not None else None)
        if key:
            prefix = self.api_key_prefix.get(
                identifier, self.api_key_prefix.get(alias) if alias is not None else None)
            if prefix:
                return "%s %s" % (prefix, key)
            else:
                return key

        return None

    def get_basic_auth_token(self) -> Optional[str]:
        """Gets HTTP basic authentication header (string).

        :return: The token for basic HTTP authentication.
        """
        username = ""
        if self.username is not None:
            username = self.username
        password = ""
        if self.password is not None:
            password = self.password

        return urllib3.util.make_headers(
            basic_auth=username + ':' + password
        ).get('authorization')

    def auth_settings(self)-> AuthSettings:
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        auth: AuthSettings = {}
        if self.access_token is not None:
            auth['bearer'] = {
                'type': 'bearer',
                'in': 'header',
                'key': 'Authorization',
                'value': 'Bearer ' + self.access_token
            }
        return auth

    def to_debug_report(self) -> str:
        """Gets the essential information for debugging.

        :return: The report for debugging.
        """
        return "Python SDK Debug Report:\n"\
               "OS: {env}\n"\
               "Python Version: {pyversion}\n"\
               "Version of the API: 1.0.0\n"\
               "SDK Package Version: 1.0.0".\
               format(env=sys.platform, pyversion=sys.version)

    def get_host_settings(self) -> List[HostSetting]:
        """Gets an array of host settings

        :return: An array of host settings
        """
        return [
            {
                'url': "http://10.254.10.7/readeck/api",
                'description': "No description provided",
            }
        ]

    def get_host_from_settings(
        self,
        index: Optional[int],
        variables: Optional[ServerVariablesT]=None,
        servers: Optional[List[HostSetting]]=None,
    ) -> str:
        """Gets host URL based on the index and variables
        :param index: array index of the host settings
        :param variables: hash of variable and the corresponding value
        :param servers: an array of host settings or None
        :return: URL based on host settings
        """
        if index is None:
            return self._base_path

        variables = {} if variables is None else variables
        servers = self.get_host_settings() if servers is None else servers

        try:
            server = servers[index]
        except IndexError:
            raise ValueError(
                "Invalid index {0} when selecting the host settings. "
                "Must be less than {1}".format(index, len(servers)))

        url = server['url']

        # go through variables and replace placeholders
        for variable_name, variable in server.get('variables', {}).items():
            used_value = variables.get(
                variable_name, variable['default_value'])

            if 'enum_values' in variable \
                    and variable['enum_values'] \
                    and used_value not in variable['enum_values']:
                raise ValueError(
                    "The variable `{0}` in the host URL has invalid value "
                    "{1}. Must be {2}.".format(
                        variable_name, variables[variable_name],
                        variable['enum_values']))

            url = url.replace("{" + variable_name + "}", used_value)

        return url

    @property
    def host(self) -> str:
        """Return generated host."""
        return self.get_host_from_settings(self.server_index, variables=self.server_variables)

    @host.setter
    def host(self, value: str) -> None:
        """Fix base path."""
        self._base_path = value
        self.server_index = None
        if self._proxy_from_env:
            # the scheme-specific proxy depends on the host, which is
            # commonly assigned after construction
            self._proxy = self._env_proxy(getproxies(), value)

    @staticmethod
    def _env_proxy(proxies: Dict[str, str], host: str) -> Optional[str]:
        """Pick the environment proxy that applies to `host`."""
        return proxies.get(urlparse(host).scheme) or proxies.get("all")

    @property
    def proxy(self) -> Optional[str]:
        """Proxy URL
        """
        return self._proxy

    @proxy.setter
    def proxy(self, value: Optional[str]) -> None:
        self._proxy = value
        self._proxy_from_env = False
