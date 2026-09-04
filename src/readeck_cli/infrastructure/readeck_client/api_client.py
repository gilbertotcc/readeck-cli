"""
    Readeck API

    # Introduction  The Readeck API provides REST endpoints that can be used for any purpose, should it be a mobile application, a script, you name it.  ## API Endpoint  You can access this API on `http://10.254.10.7/readeck/api`.  Most of your requests and responses are using JSON as the exchange format.  ## Test the API  On this documentation, you can test every route.  If you don't provide an API token in [Authentication](#auth), you can still test all the routes but note that the given curl examples only work with an API token.  # Token Authentication  If you're writing a script for yourself, the easiest way is to [generate an API token](../profile/tokens) that you can use using the `Bearer` HTTP authorization scheme.  For example, you first request will look like:  ```sh curl -H \"Authorization: Bearer <TOKEN>\" http://10.254.10.7/readeck/api/profile ```  Or, in NodeJS:  ```js fetch(\"http://10.254.10.7/readeck/api/profile\", {     headers: {     \"Authorization\": \"Bearer <TOKEN>\",     }, }) ```   # Authentication with OAuth  If you're writing an application that requires a user to grant the application permission to access their Readeck instance, you should not ask a user to create an API Token but instead, implement the necessary OAuth flow so that your application can retrieve a token in a user friendly way.  ## Available Scopes  An OAuth token grants the application some permissions based on the requested scopes. This are the available scopes you can request:  | Name              | Description                    | | :---------------- | ------------------------------ | | `bookmarks:read`  | Read only access to bookmarks  | | `bookmarks:write` | Write only access to bookmarks | | `profile:read`    | Extended profile information   |  You can see which scope applies on each route of this documentation. A route without a scope (and not \"public\") is not available with an OAuth token.  ## Client Registration  Before you can start the authorization flow, you first need to register a client on the Readeck instance.  <details> <summary>Client Registration Flow</summary> <pre role=\"img\" aria-label=\"Client Registration sequence diagram\">  ┌──────┐                 ┌────────────┐  │Client│                 │Registration│  └──┬───┘                 └─────┬──────┘     │                           │     │Client Registration Request│     │POST /api/oauth/client     │     │──────────────────────────>│     │                           │     │Client Information Response│     │<──────────────────────────│  ┌──┴───┐                 ┌─────┴──────┐  │Client│                 │Registration│  └──────┘                 └────────────┘ </pre> </details>  Readeck implement [OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591). You can register a client by querying the [Client Creation Route](#post-/oauth/client).  Upon registration, you'll receive a `client_id` that you can use in the next authorization step.  Unlike more traditional client implementations, Readeck OAuth clients are ephemeral:  - You **must** register a new client each time you start an authorization flow. - The Client is valid for 10 minutes after creation.  ## OAuth Authorization Code Flow  The Authorization Code Flow is used by clients to exchange an authorization code for an access token.  After the user returns to the client via the redirect URL, the application will get the authorization code from the URL and use it to request an access token.  This flow can only be used when, on the same device, the client can:  - send the user to the authorization page - process the redirect URL to retrieve the authorization code  On a device without a browser, a client can use the [Device Code Flow](#overview--oauth-device-code-flow).  <details> <summary>Authorization Code Flow</summary>  <pre role=\"img\" aria-label=\"Authorization Code sequence diagram\">  ┌────┐            ┌──────┐                               ┌─────────────┐      ┌───┐  │User│            │Client│                               │Authorization│      │API│  └─┬──┘            └──┬───┘                               └──────┬──────┘      └─┬─┘    │                  │                                          │               │    │Enter instance URL│                                          │               │    │─────────────────>│                                          │               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Generate PKCE verifier and challenge  │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │        Open Authorization URL            │               │    │                  │        GET /authorize?...                │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │         Redirect to login/authorization prompt              │               │    │<────────────────────────────────────────────────────────────│               │    │                  │                                          │               │    │Authorize Client                                             │               │    │POST /authorize?...                                          │               │    │────────────────────────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │          Authorization Code              │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Check state                           │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │Request Token (with code and verifier)    │               │    │                  │POST /api/oauth/token                     │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │                                          │──┐            │    │                  │                                          │  │ Check PKCE │    │                  │                                          │<─┘            │    │                  │                                          │               │    │                  │             Access Token                 │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │         Request data with Access Token   │               │    │                  │─────────────────────────────────────────────────────────>│    │                  │                                          │               │    │                  │                    Response              │               │    │                  │<─────────────────────────────────────────────────────────│  ┌─┴──┐            ┌──┴───┐                               ┌──────┴──────┐      ┌─┴─┐  │User│            │Client│                               │Authorization│      │API│  └────┘            └──────┘                               └─────────────┘      └───┘ </pre>  </details>  With a `client_id`, you can use the authorization code flow. You first need to build an authorization URL.  ### Authorization  The authorization URL is: `http://10.254.10.7/readeck/authorize` and it receives the following query parameters:  | Name                    | Description                                                                  | | :---------------------- | :--------------------------------------------------------------------------- | | `client_id`             | OAuth Client ID                                                              | | `redirect_uri`          | Redirection URI (must match exactly one given during client registration)    | | `scope`                 | Space separated list of [scopes](#overview--available-scopes). At least one. | | `code_challenge`        | [PKCE](#overview--pkce) Challenge (mandatory)                                | | `code_challenge_method` | Only `S256` is allowed                                                       | | `state`                 | Optional [client state](#overview--state)                                    |  Sending a state is not mandatory but strongly advised to prevent cross site request forgery.  ### Authorization result  Once a user grants or denies an authorization request, it will be redirected to the `redirect_uri` with the following query parameters:  | Name    | Description                                                           | | :------ | :-------------------------------------------------------------------- | | `code`  | The authorization code that the client must pass to the token request | | `state` | The state as initially set by the client                              |  In case of error (request denied by the user or something else), the redirection contains the following query parameters:  | Name                | Description                                              | | :------------------ | :------------------------------------------------------- | | `error`             | Error code (can be `invalid_request` or `access_denied`) | | `error_description` | Error description                                        | | `state`             | The state as initially set by the client                 |  Once you receive a code, you can proceed to the [Token Request](#post-/oauth/token) to eventually receive an access token that will let you use the API.  ### PKCE  The authorization code flow requires that you use [PKCE](https://datatracker.ietf.org/doc/html/rfc7636) with an S256 method only (the \"plain\" method is not allowed).  1. The client creates a random **verifier** and produces a SHA-256 hash that is encoded in base64 to make a **challenge**. 2. The **challenge** is added to the authorization URL as `code_challenge` query parameter. 3. When requesting the token, the client sends the **verifier** as `code_verifier` parameter. Then the server, that kept track of the challenge can check it matches the received verifier.  **Important**: The challenge must be base64 encoded, **with URL encoding** and **without padding**.  <details part=\"details\"> <summary>Javascript example of a verifier and challenge generation</summary>  ```js // This generates a 64 character long random alphanumeric string. function generateRandomString() {   const alphabet =     \"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\"   let res = \"\"   const buf = new Uint8Array(64)   crypto.getRandomValues(buf)   for (let i in buf) {     res += alphabet[buf[i] % alphabet.length]   }   return res }  // This hashes the verifier and encodes the hash to URL safe base64. async function pkceChallengeFromVerifier(v) {   const b = await crypto.subtle.digest(\"SHA-256\", new TextEncoder().encode(v))   return btoa(String.fromCharCode(...new Uint8Array(b)))     .replaceAll(\"+\", \"-\")     .replaceAll(\"/\", \"_\")     .replaceAll(\"=\", \"\") }  const verifier = generateRandomString() pkceChallengeFromVerifier(verifier).then((challenge) => {   console.log(verifier)   console.log(challenge) }) ```  </details>  ### State  The `state` parameter that the client can add to the authorization URL is for the client only. When present, it is sent back in the redirection URI that contains the authorization code. The client can keep track of it and check it matches its initial value. It is strongly recommended to use it.  ## OAuth Device Code Flow  The Device Code Flow is used by browserless or input-constrained devices in the device flow to exchange a previously obtained device code for an access token. An e-reader is a good candidate for using this flow.  <details> <summary>Device Code Flow</summary> <pre role=\"img\" aria-label=\"Device Code sequence diagram\">  ┌────┐               ┌──────┐                         ┌─────────────┐  │User│               │Client│                         │Authorization│  └─┬──┘               └──┬───┘                         └──────┬──────┘    │                     │                                    │    │                     │(1) Request device code             │    │                     │───────────────────────────────────>│    │                     │                                    │    │                     │(2) Return device code, user code,  │    │                     │URL and interval                    │    │                     │<───────────────────────────────────│    │                     │                                    │    │(3) Provide user code│                                    │    │    and URL to user  │                                    │    │ <───────────────────│                                    │    │                   ┌────┐───────────────────────────────────┐    │                   │Loop│                                 │ │    │                   └────┘                                 │ │    │                   │ │                                    │ │    │                   │ │(4) Poll for authorization          │ │    │                   │ │───────────────────────────────────>│ │    │                   │ │                                    │ │    │                   │ │               authorization_pending│ │    │                   │ │<───────────────────────────────────│ │    │                   │ │                                    │ │    │                   └────────────────────────────────────────┘    │                     │                                    │    │(5) Open authorization URL and enter user code            │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │(5) Approve client access                                 │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │                     │             (6) Return access_token│    │                     │<───────────────────────────────────│    │                     │                                    │  ┌─┴──┐               ┌──┴───┐                         ┌──────┴──────┐  │User│               │Client│                         │Authorization│  └────┘               └──────┘                         └─────────────┘ </pre> </details>  1. The client request access from Readeck on the [Device Authorization route](#post-/oauth/device) 2. Readeck issues a device code, an end-user code and provides the end-user verification URI. This information is valid for 5 minutes. 3. The client instructs the user to visit the provided end-user verification URI. The client provides the user with the end-user code to enter in order to review the authorization request. 4. While the user reviews the client's request (step 5), the client repeatedly polls the [Token route](#post-/oauth/token) to find out if the user completed the user authorization step. The client includes the device code and its client identifier. The token route can only be polled every 5 seconds. 5. After authentication, Readeck prompts the user to input the user code provided by the device client and prompts the user to accept or decline the request. 6. Readeck validates the device code provided by the client and responds with the access token if the client is granted access, an error if they are denied access, or a pending state, indicating that the client should continue to poll.  <details> <summary>Python example of the device flow</summary>  ```python import json import time  import httpx   def main():     client = httpx.Client(         base_url=\"http://10.254.10.7/readeck\",         headers={\"Accept\": \"application/json\"},     )      # Create a client     rsp = client.post(         \"api/oauth/client\",         data={             \"client_name\": \"Test App\",             \"client_uri\": \"https://example.net/\",             \"software_id\": uuid.uuid4(),             \"software_version\": \"1.0.2\",             \"grant_types\": [\"urn:ietf:params:oauth:grant-type:device_code\"],         },     )     rsp.raise_for_status()     client_id = rsp.json()[\"client_id\"]      # Get user code.     rsp = client.post(         \"api/oauth/device\",         data={             \"client_id\": client_id,             \"scope\": \"bookmarks:read bookmarks:write\",         },     )     rsp.raise_for_status()      req_data = rsp.json()      # The client keeps the device code for itself.     device_code = req_data[\"device_code\"]      # User code with a separator for better readability     user_code = f\"{req_data['user_code'][0:4]}-{req_data['user_code'][4:]}\"      # Refresh interval     interval = req_data[\"interval\"]      # Information the client must provide the user with.     print(f\"CODE         : {user_code}\")     print(f\"URL          : {req_data['verification_uri']}\")     print(f\"COMPLETE URL : {req_data['verification_uri_complete']}\")      # Now, the client waits for the user to accept or deny     # the authorization request.     wait = 0     while True:         if wait > 0:             # wait before the request so we can use continue in the loop             time.sleep(wait)         else:             wait = interval          rsp = client.post(             \"api/oauth/token\",             data={                 \"grant_type\": \"urn:ietf:params:oauth:grant-type:device_code\",                 \"client_id\": client_id,                 \"device_code\": device_code,             },         )         if rsp.status_code >= 500:             rsp.raise_for_status()          data = rsp.json()          if data.get(\"access_token\"):             print(\"Token retrieved!\")             print(json.dumps(data, indent=2))             return          error = data.get(\"error\")         match error:             case \"access_denied\":                 # The user denied the request                 print(\"Access was denied\")                 return             case \"slow_down\":                 # Server asks to slow down, we'll sleep 5s                 continue             case \"authorization_pending\":                 # Still waiting                 print(\"Waiting for authorization...\")                 continue             case \"expired_token\":                 # The request has expired                 print(\"Request has expired\")                 return             case _:                 print(f\"Fatal error: {error}\")                 return   if __name__ == \"__main__\":     main() ```  </details>   

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501



import datetime
from dateutil.parser import parse
from enum import Enum
import decimal
import json
import mimetypes
import os
import re
import tempfile
import uuid

from urllib.parse import quote
from typing import Tuple, Optional, List, Dict, Union
from pydantic import SecretStr

from readeck_cli.infrastructure.readeck_client.configuration import Configuration
from readeck_cli.infrastructure.readeck_client.api_response import ApiResponse, T as ApiResponseT
import readeck_cli.infrastructure.readeck_client.models
from readeck_cli.infrastructure.readeck_client import rest
from readeck_cli.infrastructure.readeck_client.exceptions import (
    ApiValueError,
    ApiException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ServiceException
)

RequestSerialized = Tuple[str, str, Dict[str, str], Optional[str], List[str]]

class ApiClient:
    """Generic API client for OpenAPI client library builds.

    OpenAPI generic API client. This client handles the client-
    server communication, and is invariant across implementations. Specifics of
    the methods and models for each application are generated from the OpenAPI
    templates.

    :param configuration: .Configuration object for this client
    :param header_name: a header to pass when making calls to the API.
    :param header_value: a header value to pass when making calls to
        the API.
    :param cookie: a cookie to include in the header when making calls
        to the API
    """

    PRIMITIVE_TYPES = (float, bool, bytes, str, int)
    NATIVE_TYPES_MAPPING = {
        'int': int,
        'long': int, # TODO remove as only py3 is supported?
        'float': float,
        'str': str,
        'bool': bool,
        'date': datetime.date,
        'datetime': datetime.datetime,
        'decimal': decimal.Decimal,
        'UUID': uuid.UUID,
        'object': object,
    }
    _pool = None

    def __init__(
        self,
        configuration=None,
        header_name=None,
        header_value=None,
        cookie=None
    ) -> None:
        # use default configuration if none is provided
        if configuration is None:
            configuration = Configuration.get_default()
        self.configuration = configuration

        self.rest_client = rest.RESTClientObject(configuration)
        self.default_headers = {}
        if header_name is not None:
            self.default_headers[header_name] = header_value
        self.cookie = cookie
        # Set default User-Agent.
        self.user_agent = 'OpenAPI-Generator/1.0.0/python'
        self.client_side_validation = configuration.client_side_validation

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def user_agent(self):
        """User agent for this API client"""
        return self.default_headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value):
        self.default_headers['User-Agent'] = value

    def set_default_header(self, header_name, header_value):
        self.default_headers[header_name] = header_value


    _default = None

    @classmethod
    def get_default(cls):
        """Return new instance of ApiClient.

        This method returns newly created, based on default constructor,
        object of ApiClient class or returns a copy of default
        ApiClient.

        :return: The ApiClient object.
        """
        if cls._default is None:
            cls._default = ApiClient()
        return cls._default

    @classmethod
    def set_default(cls, default):
        """Set default instance of ApiClient.

        It stores default ApiClient.

        :param default: object of ApiClient.
        """
        cls._default = default

    def param_serialize(
        self,
        method,
        resource_path,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None, auth_settings=None,
        collection_formats=None,
        _host=None,
        _request_auth=None
    ) -> RequestSerialized:

        """Builds the HTTP request params needed by the request.
        :param method: Method to call.
        :param resource_path: Path to method endpoint.
        :param path_params: Path parameters in the url.
        :param query_params: Query parameters in the url.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param auth_settings list: Auth Settings names for the request.
        :param files dict: key -> filename, value -> filepath,
            for `multipart/form-data`.
        :param collection_formats: dict of collection formats for path, query,
            header, and post parameters.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :return: tuple of form (path, http_method, query_params, header_params,
            body, post_params, files)
        """

        config = self.configuration

        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if self.cookie:
            header_params['Cookie'] = self.cookie
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(
                self.parameters_to_tuples(header_params,collection_formats)
            )

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            path_params = self.parameters_to_tuples(
                path_params,
                collection_formats
            )
            for k, v in path_params:
                # specified safe chars, encode everything
                resource_path = resource_path.replace(
                    '{%s}' % k,
                    quote(str(v), safe=config.safe_chars_for_path_param)
                )

        # post parameters
        if post_params or files:
            post_params = post_params if post_params else []
            post_params = self.sanitize_for_serialization(post_params)
            post_params = self.parameters_to_tuples(
                post_params,
                collection_formats
            )
            if files:
                post_params.extend(self.files_parameters(files))

        # auth setting
        self.update_params_for_auth(
            header_params,
            query_params,
            auth_settings,
            resource_path,
            method,
            body,
            request_auth=_request_auth
        )

        # body
        if body:
            body = self.sanitize_for_serialization(body)

        # request url
        if _host is None or self.configuration.ignore_operation_servers:
            url = self.configuration.host + resource_path
        else:
            # use server/host defined in path or operation instead
            url = _host + resource_path

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            url_query = self.parameters_to_url_query(
                query_params,
                collection_formats
            )
            url += "?" + url_query

        return method, url, header_params, body, post_params

    def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None
    ) -> rest.RESTResponse:
        """Makes the HTTP request (synchronous)
        :param method: Method to call.
        :param url: Path to method endpoint.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param _request_timeout: timeout setting for this request.
        :return: RESTResponse
        """

        try:
            # perform request and return response
            response_data = self.rest_client.request(
                method, url,
                headers=header_params,
                body=body, post_params=post_params,
                _request_timeout=_request_timeout
            )

        except ApiException as e:
            raise e

        return response_data

    def response_deserialize(
        self,
        response_data: rest.RESTResponse,
        response_types_map: Optional[Dict[str, ApiResponseT]]=None
    ) -> ApiResponse[ApiResponseT]:
        """Deserializes response into an object.
        :param response_data: RESTResponse object to be deserialized.
        :param response_types_map: dict of response types.
        :return: ApiResponse
        """

        msg = "RESTResponse.read() must be called before passing it to response_deserialize()"
        assert response_data.data is not None, msg

        response_type = response_types_map.get(str(response_data.status), None)
        if not response_type and isinstance(response_data.status, int) and 100 <= response_data.status <= 599:
            # if not found, look for '1XX', '2XX', etc.
            response_type = response_types_map.get(str(response_data.status)[0] + "XX", None)

        # If the response_type has not matched (eg. did not match the previous if statements) and the default response is available, use it.
        if response_type is None and str(response_data.status) not in response_types_map \
            and (not isinstance(response_data.status, int) or not 100 <= response_data.status <= 599 or str(response_data.status)[0] + "XX" not in response_types_map) \
            and 'default' in response_types_map:
            response_type = response_types_map['default']

        # deserialize response data
        response_text = None
        return_data = None
        try:
            if response_type in ("bytearray", "bytes"):
                return_data = response_data.data
            elif response_type == "file":
                return_data = self.__deserialize_file(response_data)
            elif response_type is not None:
                match = None
                content_type = response_data.headers.get('content-type')
                if content_type is not None:
                    match = re.search(r"charset=([a-zA-Z\-\d]+)[\s;]?", content_type)
                encoding = match.group(1) if match else "utf-8"
                response_text = response_data.data.decode(encoding)
                return_data = self.deserialize(response_text, response_type, content_type)
        finally:
            if not 200 <= response_data.status <= 299:
                raise ApiException.from_response(
                    http_resp=response_data,
                    body=response_text,
                    data=return_data,
                )

        return ApiResponse(
            status_code = response_data.status,
            data = return_data,
            headers = response_data.headers,
            raw_data = response_data.data
        )

    def sanitize_for_serialization(self, obj):
        """Builds a JSON POST object.

        If obj is None, return None.
        If obj is SecretStr, return obj.get_secret_value()
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is decimal.Decimal return string representation.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is OpenAPI model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, SecretStr):
            return obj.get_secret_value()
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, list):
            return [
                self.sanitize_for_serialization(sub_obj) for sub_obj in obj
            ]
        elif isinstance(obj, tuple):
            return tuple(
                self.sanitize_for_serialization(sub_obj) for sub_obj in obj
            )
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, dict):
            return {
                key: self.sanitize_for_serialization(val)
                for key, val in obj.items()
            }

        # Convert model obj to dict except
        # attributes `openapi_types`, `attribute_map`
        # and attributes which value is not None.
        # Convert attribute name to json key in
        # model definition for request.
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            obj_dict = obj.to_dict()
        else:
            obj_dict = obj.__dict__

        return self.sanitize_for_serialization(obj_dict)


    def deserialize(self, response_text: str, response_type: str, content_type: Optional[str]):
        """Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialized object, or string of class name.
        :param content_type: content type of response.

        :return: deserialized object.
        """

        # fetch data from response object
        if content_type is None:
            try:
                data = json.loads(response_text)
            except ValueError:
                data = response_text
        elif re.match(r'^application/(json|[\w!#$&.+\-^_]+\+json)\s*(;|$)', content_type, re.IGNORECASE):
            if response_text == "":
                data = ""
            else:
                data = json.loads(response_text)
        elif re.match(r'^text\/[a-z.+-]+\s*(;|$)', content_type, re.IGNORECASE):
            data = response_text
        else:
            raise ApiException(
                status=0,
                reason="Unsupported content type: {0}".format(content_type)
            )

        return self.__deserialize(data, response_type)

    def __deserialize(self, data, klass):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if isinstance(klass, str):
            if klass.startswith('Optional['):
                m = re.match(r'Optional\[(.*)]', klass)
                assert m is not None, "Malformed Optional type definition"
                # data is not None here, so the optionality is already resolved
                return self.__deserialize(data, m.group(1))

            if klass.startswith('List['):
                m = re.match(r'List\[(.*)]', klass)
                assert m is not None, "Malformed List type definition"
                sub_kls = m.group(1)
                return [self.__deserialize(sub_data, sub_kls)
                        for sub_data in data]

            if klass.startswith('Dict['):
                m = re.match(r'Dict\[([^,]*), (.*)]', klass)
                assert m is not None, "Malformed Dict type definition"
                sub_kls = m.group(2)
                return {k: self.__deserialize(v, sub_kls)
                        for k, v in data.items()}

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                klass = getattr(readeck_cli.infrastructure.readeck_client.models, klass)

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)
        elif klass is object:
            return self.__deserialize_object(data)
        elif klass is datetime.date:
            return self.__deserialize_date(data)
        elif klass is datetime.datetime:
            return self.__deserialize_datetime(data)
        elif klass is decimal.Decimal:
            return decimal.Decimal(data)
        elif klass is uuid.UUID:
            return uuid.UUID(data)
        elif issubclass(klass, Enum):
            return self.__deserialize_enum(data, klass)
        else:
            return self.__deserialize_model(data, klass)

    def parameters_to_tuples(self, params, collection_formats):
        """Get parameters as list of tuples, formatting collections.

        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params: List[Tuple[str, str]] = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in params.items() if isinstance(params, dict) else params:
            if isinstance(v, bool):
                v = str(v).lower()
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend(
                        (k, str(value).lower() if isinstance(value, bool) else value)
                        for value in v
                    )
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(
                            str(value).lower() if isinstance(value, bool) else str(value)
                            for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    def parameters_to_url_query(self, params, collection_formats):
        """Get parameters as list of tuples, formatting collections.

        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: URL query string (e.g. a=Hello%20World&b=123)
        """
        new_params: List[Tuple[str, str]] = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in params.items() if isinstance(params, dict) else params:
            if isinstance(v, bool):
                v = str(v).lower()
            if isinstance(v, (int, float)):
                v = str(v)
            if isinstance(v, dict):
                v = json.dumps(v)

            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend(
                        (k, quote(str(value).lower() if isinstance(value, bool) else str(value)))
                        for value in v
                    )
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(
                            quote(str(value).lower() if isinstance(value, bool) else str(value))
                            for value in v))
                    )
            else:
                new_params.append((k, quote(str(v))))

        return "&".join(["=".join(map(str, item)) for item in new_params])

    def files_parameters(
        self,
        files: Dict[str, Union[str, bytes, List[str], List[bytes], Tuple[str, bytes]]],
    ):
        """Builds form parameters.

        :param files: File parameters.
        :return: Form parameters with files.
        """
        params = []
        for k, v in files.items():
            if isinstance(v, str):
                with open(v, 'rb') as f:
                    filename = os.path.basename(f.name)
                    filedata = f.read()
            elif isinstance(v, bytes):
                filename = k
                filedata = v
            elif isinstance(v, tuple):
                filename, filedata = v
            elif isinstance(v, list):
                for file_param in v:
                    params.extend(self.files_parameters({k: file_param}))
                continue
            else:
                raise ValueError("Unsupported file value")
            mimetype = (
                mimetypes.guess_type(filename)[0]
                or 'application/octet-stream'
            )
            params.append(
                tuple([k, tuple([filename, filedata, mimetype])])
            )
        return params

    def select_header_accept(self, accepts: List[str]) -> Optional[str]:
        """Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return None

        for accept in accepts:
            if re.search('json', accept, re.IGNORECASE):
                return accept

        return accepts[0]

    def select_header_content_type(self, content_types):
        """Returns `Content-Type` based on an array of content_types provided.

        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return None

        for content_type in content_types:
            if re.search('json', content_type, re.IGNORECASE):
                return content_type

        return content_types[0]

    def update_params_for_auth(
        self,
        headers,
        queries,
        auth_settings,
        resource_path,
        method,
        body,
        request_auth=None
    ) -> None:
        """Updates header and query params based on authentication setting.

        :param headers: Header parameters dict to be updated.
        :param queries: Query parameters tuple list to be updated.
        :param auth_settings: Authentication setting identifiers list.
        :resource_path: A string representation of the HTTP request resource path.
        :method: A string representation of the HTTP request method.
        :body: A object representing the body of the HTTP request.
        The object type is the return value of sanitize_for_serialization().
        :param request_auth: if set, the provided settings will
                             override the token in the configuration.
        """
        if not auth_settings:
            return

        if request_auth:
            self._apply_auth_params(
                headers,
                queries,
                resource_path,
                method,
                body,
                request_auth
            )
        else:
            for auth in auth_settings:
                auth_setting = self.configuration.auth_settings().get(auth)
                if auth_setting:
                    self._apply_auth_params(
                        headers,
                        queries,
                        resource_path,
                        method,
                        body,
                        auth_setting
                    )

    def _apply_auth_params(
        self,
        headers,
        queries,
        resource_path,
        method,
        body,
        auth_setting
    ) -> None:
        """Updates the request parameters based on a single auth_setting

        :param headers: Header parameters dict to be updated.
        :param queries: Query parameters tuple list to be updated.
        :resource_path: A string representation of the HTTP request resource path.
        :method: A string representation of the HTTP request method.
        :body: A object representing the body of the HTTP request.
        The object type is the return value of sanitize_for_serialization().
        :param auth_setting: auth settings for the endpoint
        """
        if auth_setting['in'] == 'cookie':
            if not 'Cookie' in headers:
                headers['Cookie'] = ""
            else:
                headers['Cookie'] += "; "
            # Account for cookie value containing spaces and special characters, excluding base64 delimiters
            cookie_value = quote(str(auth_setting['value']), safe="!#$%&'()*+-./:<=>?@[]^_`{|}~%+/=")
            headers['Cookie'] += f"{auth_setting['key']}={cookie_value}"
        elif auth_setting['in'] == 'header':
            if auth_setting['type'] != 'http-signature':
                headers[auth_setting['key']] = auth_setting['value']
        elif auth_setting['in'] == 'query':
            queries.append((auth_setting['key'], auth_setting['value']))
        else:
            raise ApiValueError(
                'Authentication token must be in `query` or `header`'
            )

    def __deserialize_file(self, response):
        """Deserializes body to file

        Saves response body into a file in a temporary folder,
        using the filename from the `Content-Disposition` header if provided.

        handle file downloading
        save response body into a tmp file and return the instance

        :param response:  RESTResponse.
        :return: file path.
        """
        fd, path = tempfile.mkstemp(dir=self.configuration.temp_folder_path)
        os.close(fd)
        os.remove(path)

        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            m = re.search(
                r'filename=[\'"]?([^\'"\s]+)[\'"]?',
                content_disposition
            )
            assert m is not None, "Unexpected 'content-disposition' header value"
            filename = os.path.basename(m.group(1))  # Strip any directory traversal
            if filename in ("", ".", ".."):  # fall back to tmp filename
                filename = os.path.basename(path)
            path = os.path.join(os.path.dirname(path), filename)

        with open(path, "wb") as f:
            f.write(response.data)

        return path

    def __deserialize_primitive(self, data, klass):
        """Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, long, float, str, bool.
        """
        try:
            return klass(data)
        except UnicodeEncodeError:
            return str(data)
        except TypeError:
            return data

    def __deserialize_object(self, value):
        """Return an original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise rest.ApiException(
                status=0,
                reason="Failed to parse `{0}` as date object".format(string)
            )

    def __deserialize_datetime(self, string):
        """Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise rest.ApiException(
                status=0,
                reason=(
                    "Failed to parse `{0}` as datetime object"
                    .format(string)
                )
            )

    def __deserialize_enum(self, data, klass):
        """Deserializes primitive type to enum.

        :param data: primitive type.
        :param klass: class literal.
        :return: enum value.
        """
        try:
            return klass(data)
        except ValueError:
            raise rest.ApiException(
                status=0,
                reason=(
                    "Failed to parse `{0}` as `{1}`"
                    .format(data, klass)
                )
            )

    def __deserialize_model(self, data, klass):
        """Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """

        return klass.from_dict(data)
