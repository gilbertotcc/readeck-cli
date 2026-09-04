# coding: utf-8

"""
    Readeck API

    # Introduction  The Readeck API provides REST endpoints that can be used for any purpose, should it be a mobile application, a script, you name it.  ## API Endpoint  You can access this API on `http://10.254.10.7/readeck/api`.  Most of your requests and responses are using JSON as the exchange format.  ## Test the API  On this documentation, you can test every route.  If you don't provide an API token in [Authentication](#auth), you can still test all the routes but note that the given curl examples only work with an API token.  # Token Authentication  If you're writing a script for yourself, the easiest way is to [generate an API token](../profile/tokens) that you can use using the `Bearer` HTTP authorization scheme.  For example, you first request will look like:  ```sh curl -H \"Authorization: Bearer <TOKEN>\" http://10.254.10.7/readeck/api/profile ```  Or, in NodeJS:  ```js fetch(\"http://10.254.10.7/readeck/api/profile\", {     headers: {     \"Authorization\": \"Bearer <TOKEN>\",     }, }) ```   # Authentication with OAuth  If you're writing an application that requires a user to grant the application permission to access their Readeck instance, you should not ask a user to create an API Token but instead, implement the necessary OAuth flow so that your application can retrieve a token in a user friendly way.  ## Available Scopes  An OAuth token grants the application some permissions based on the requested scopes. This are the available scopes you can request:  | Name              | Description                    | | :---------------- | ------------------------------ | | `bookmarks:read`  | Read only access to bookmarks  | | `bookmarks:write` | Write only access to bookmarks | | `profile:read`    | Extended profile information   |  You can see which scope applies on each route of this documentation. A route without a scope (and not \"public\") is not available with an OAuth token.  ## Client Registration  Before you can start the authorization flow, you first need to register a client on the Readeck instance.  <details> <summary>Client Registration Flow</summary> <pre role=\"img\" aria-label=\"Client Registration sequence diagram\">  ┌──────┐                 ┌────────────┐  │Client│                 │Registration│  └──┬───┘                 └─────┬──────┘     │                           │     │Client Registration Request│     │POST /api/oauth/client     │     │──────────────────────────>│     │                           │     │Client Information Response│     │<──────────────────────────│  ┌──┴───┐                 ┌─────┴──────┐  │Client│                 │Registration│  └──────┘                 └────────────┘ </pre> </details>  Readeck implement [OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591). You can register a client by querying the [Client Creation Route](#post-/oauth/client).  Upon registration, you'll receive a `client_id` that you can use in the next authorization step.  Unlike more traditional client implementations, Readeck OAuth clients are ephemeral:  - You **must** register a new client each time you start an authorization flow. - The Client is valid for 10 minutes after creation.  ## OAuth Authorization Code Flow  The Authorization Code Flow is used by clients to exchange an authorization code for an access token.  After the user returns to the client via the redirect URL, the application will get the authorization code from the URL and use it to request an access token.  This flow can only be used when, on the same device, the client can:  - send the user to the authorization page - process the redirect URL to retrieve the authorization code  On a device without a browser, a client can use the [Device Code Flow](#overview--oauth-device-code-flow).  <details> <summary>Authorization Code Flow</summary>  <pre role=\"img\" aria-label=\"Authorization Code sequence diagram\">  ┌────┐            ┌──────┐                               ┌─────────────┐      ┌───┐  │User│            │Client│                               │Authorization│      │API│  └─┬──┘            └──┬───┘                               └──────┬──────┘      └─┬─┘    │                  │                                          │               │    │Enter instance URL│                                          │               │    │─────────────────>│                                          │               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Generate PKCE verifier and challenge  │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │        Open Authorization URL            │               │    │                  │        GET /authorize?...                │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │         Redirect to login/authorization prompt              │               │    │<────────────────────────────────────────────────────────────│               │    │                  │                                          │               │    │Authorize Client                                             │               │    │POST /authorize?...                                          │               │    │────────────────────────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │          Authorization Code              │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │──┐                                       │               │    │                  │  │ Check state                           │               │    │                  │<─┘                                       │               │    │                  │                                          │               │    │                  │Request Token (with code and verifier)    │               │    │                  │POST /api/oauth/token                     │               │    │                  │─────────────────────────────────────────>│               │    │                  │                                          │               │    │                  │                                          │──┐            │    │                  │                                          │  │ Check PKCE │    │                  │                                          │<─┘            │    │                  │                                          │               │    │                  │             Access Token                 │               │    │                  │<─────────────────────────────────────────│               │    │                  │                                          │               │    │                  │         Request data with Access Token   │               │    │                  │─────────────────────────────────────────────────────────>│    │                  │                                          │               │    │                  │                    Response              │               │    │                  │<─────────────────────────────────────────────────────────│  ┌─┴──┐            ┌──┴───┐                               ┌──────┴──────┐      ┌─┴─┐  │User│            │Client│                               │Authorization│      │API│  └────┘            └──────┘                               └─────────────┘      └───┘ </pre>  </details>  With a `client_id`, you can use the authorization code flow. You first need to build an authorization URL.  ### Authorization  The authorization URL is: `http://10.254.10.7/readeck/authorize` and it receives the following query parameters:  | Name                    | Description                                                                  | | :---------------------- | :--------------------------------------------------------------------------- | | `client_id`             | OAuth Client ID                                                              | | `redirect_uri`          | Redirection URI (must match exactly one given during client registration)    | | `scope`                 | Space separated list of [scopes](#overview--available-scopes). At least one. | | `code_challenge`        | [PKCE](#overview--pkce) Challenge (mandatory)                                | | `code_challenge_method` | Only `S256` is allowed                                                       | | `state`                 | Optional [client state](#overview--state)                                    |  Sending a state is not mandatory but strongly advised to prevent cross site request forgery.  ### Authorization result  Once a user grants or denies an authorization request, it will be redirected to the `redirect_uri` with the following query parameters:  | Name    | Description                                                           | | :------ | :-------------------------------------------------------------------- | | `code`  | The authorization code that the client must pass to the token request | | `state` | The state as initially set by the client                              |  In case of error (request denied by the user or something else), the redirection contains the following query parameters:  | Name                | Description                                              | | :------------------ | :------------------------------------------------------- | | `error`             | Error code (can be `invalid_request` or `access_denied`) | | `error_description` | Error description                                        | | `state`             | The state as initially set by the client                 |  Once you receive a code, you can proceed to the [Token Request](#post-/oauth/token) to eventually receive an access token that will let you use the API.  ### PKCE  The authorization code flow requires that you use [PKCE](https://datatracker.ietf.org/doc/html/rfc7636) with an S256 method only (the \"plain\" method is not allowed).  1. The client creates a random **verifier** and produces a SHA-256 hash that is encoded in base64 to make a **challenge**. 2. The **challenge** is added to the authorization URL as `code_challenge` query parameter. 3. When requesting the token, the client sends the **verifier** as `code_verifier` parameter. Then the server, that kept track of the challenge can check it matches the received verifier.  **Important**: The challenge must be base64 encoded, **with URL encoding** and **without padding**.  <details part=\"details\"> <summary>Javascript example of a verifier and challenge generation</summary>  ```js // This generates a 64 character long random alphanumeric string. function generateRandomString() {   const alphabet =     \"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\"   let res = \"\"   const buf = new Uint8Array(64)   crypto.getRandomValues(buf)   for (let i in buf) {     res += alphabet[buf[i] % alphabet.length]   }   return res }  // This hashes the verifier and encodes the hash to URL safe base64. async function pkceChallengeFromVerifier(v) {   const b = await crypto.subtle.digest(\"SHA-256\", new TextEncoder().encode(v))   return btoa(String.fromCharCode(...new Uint8Array(b)))     .replaceAll(\"+\", \"-\")     .replaceAll(\"/\", \"_\")     .replaceAll(\"=\", \"\") }  const verifier = generateRandomString() pkceChallengeFromVerifier(verifier).then((challenge) => {   console.log(verifier)   console.log(challenge) }) ```  </details>  ### State  The `state` parameter that the client can add to the authorization URL is for the client only. When present, it is sent back in the redirection URI that contains the authorization code. The client can keep track of it and check it matches its initial value. It is strongly recommended to use it.  ## OAuth Device Code Flow  The Device Code Flow is used by browserless or input-constrained devices in the device flow to exchange a previously obtained device code for an access token. An e-reader is a good candidate for using this flow.  <details> <summary>Device Code Flow</summary> <pre role=\"img\" aria-label=\"Device Code sequence diagram\">  ┌────┐               ┌──────┐                         ┌─────────────┐  │User│               │Client│                         │Authorization│  └─┬──┘               └──┬───┘                         └──────┬──────┘    │                     │                                    │    │                     │(1) Request device code             │    │                     │───────────────────────────────────>│    │                     │                                    │    │                     │(2) Return device code, user code,  │    │                     │URL and interval                    │    │                     │<───────────────────────────────────│    │                     │                                    │    │(3) Provide user code│                                    │    │    and URL to user  │                                    │    │ <───────────────────│                                    │    │                   ┌────┐───────────────────────────────────┐    │                   │Loop│                                 │ │    │                   └────┘                                 │ │    │                   │ │                                    │ │    │                   │ │(4) Poll for authorization          │ │    │                   │ │───────────────────────────────────>│ │    │                   │ │                                    │ │    │                   │ │               authorization_pending│ │    │                   │ │<───────────────────────────────────│ │    │                   │ │                                    │ │    │                   └────────────────────────────────────────┘    │                     │                                    │    │(5) Open authorization URL and enter user code            │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │(5) Approve client access                                 │    ├ ────────────────────────────────────────────────────────>│    │                     │                                    │    │                     │             (6) Return access_token│    │                     │<───────────────────────────────────│    │                     │                                    │  ┌─┴──┐               ┌──┴───┐                         ┌──────┴──────┐  │User│               │Client│                         │Authorization│  └────┘               └──────┘                         └─────────────┘ </pre> </details>  1. The client request access from Readeck on the [Device Authorization route](#post-/oauth/device) 2. Readeck issues a device code, an end-user code and provides the end-user verification URI. This information is valid for 5 minutes. 3. The client instructs the user to visit the provided end-user verification URI. The client provides the user with the end-user code to enter in order to review the authorization request. 4. While the user reviews the client's request (step 5), the client repeatedly polls the [Token route](#post-/oauth/token) to find out if the user completed the user authorization step. The client includes the device code and its client identifier. The token route can only be polled every 5 seconds. 5. After authentication, Readeck prompts the user to input the user code provided by the device client and prompts the user to accept or decline the request. 6. Readeck validates the device code provided by the client and responds with the access token if the client is granted access, an error if they are denied access, or a pending state, indicating that the client should continue to poll.  <details> <summary>Python example of the device flow</summary>  ```python import json import time  import httpx   def main():     client = httpx.Client(         base_url=\"http://10.254.10.7/readeck\",         headers={\"Accept\": \"application/json\"},     )      # Create a client     rsp = client.post(         \"api/oauth/client\",         data={             \"client_name\": \"Test App\",             \"client_uri\": \"https://example.net/\",             \"software_id\": uuid.uuid4(),             \"software_version\": \"1.0.2\",             \"grant_types\": [\"urn:ietf:params:oauth:grant-type:device_code\"],         },     )     rsp.raise_for_status()     client_id = rsp.json()[\"client_id\"]      # Get user code.     rsp = client.post(         \"api/oauth/device\",         data={             \"client_id\": client_id,             \"scope\": \"bookmarks:read bookmarks:write\",         },     )     rsp.raise_for_status()      req_data = rsp.json()      # The client keeps the device code for itself.     device_code = req_data[\"device_code\"]      # User code with a separator for better readability     user_code = f\"{req_data['user_code'][0:4]}-{req_data['user_code'][4:]}\"      # Refresh interval     interval = req_data[\"interval\"]      # Information the client must provide the user with.     print(f\"CODE         : {user_code}\")     print(f\"URL          : {req_data['verification_uri']}\")     print(f\"COMPLETE URL : {req_data['verification_uri_complete']}\")      # Now, the client waits for the user to accept or deny     # the authorization request.     wait = 0     while True:         if wait > 0:             # wait before the request so we can use continue in the loop             time.sleep(wait)         else:             wait = interval          rsp = client.post(             \"api/oauth/token\",             data={                 \"grant_type\": \"urn:ietf:params:oauth:grant-type:device_code\",                 \"client_id\": client_id,                 \"device_code\": device_code,             },         )         if rsp.status_code >= 500:             rsp.raise_for_status()          data = rsp.json()          if data.get(\"access_token\"):             print(\"Token retrieved!\")             print(json.dumps(data, indent=2))             return          error = data.get(\"error\")         match error:             case \"access_denied\":                 # The user denied the request                 print(\"Access was denied\")                 return             case \"slow_down\":                 # Server asks to slow down, we'll sleep 5s                 continue             case \"authorization_pending\":                 # Still waiting                 print(\"Waiting for authorization...\")                 continue             case \"expired_token\":                 # The request has expired                 print(\"Request has expired\")                 return             case _:                 print(f\"Fatal error: {error}\")                 return   if __name__ == \"__main__\":     main() ```  </details>   

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import ipaddress
import io
import json
import re
import ssl
from urllib.parse import urlparse

import urllib3

from readeck_cli.infrastructure.readeck_client.exceptions import ApiException, ApiValueError

SUPPORTED_SOCKS_PROXIES = {"socks5", "socks5h", "socks4", "socks4a"}
RESTResponseType = urllib3.HTTPResponse


def is_socks_proxy_url(url):
    if url is None:
        return False
    split_section = url.split("://")
    if len(split_section) < 2:
        return False
    else:
        return split_section[0].lower() in SUPPORTED_SOCKS_PROXIES

def contenttype_matches(contenttype, maintype, subtype):
    """Matches the given contenttype against the given type and subtype

    :param contenttype: the content type to match
    :param maintype: the expected maintype
    :param subtype: the expected subtype
    :return: `true` when the given content type matches the given type and subtype,
        regardless of the presence of mime type parameters, otherwise returns `false`.
    :rtype: bool
    """
    pattern = '{type}/(?:[^+;]+\\+)?{subtype}(?:[ \t]*;.*)?'.format(
        type = re.escape(maintype),
        subtype = re.escape(subtype),
    )
    return re.fullmatch(pattern, contenttype, re.IGNORECASE) is not None

def should_bypass_proxies(url: str, no_proxy: str) -> bool:
    """Return whether ``url`` matches the comma-separated ``no_proxy`` rules."""
    parsed_url = urlparse(url)
    if not parsed_url.hostname:
        return True

    host = parsed_url.hostname.lower()
    host_and_port = parsed_url.netloc.lower()
    try:
        host_ip = ipaddress.ip_address(host)
    except ValueError:
        host_ip = None

    for entry in (entry.strip().lower() for entry in no_proxy.split(',')):
        if not entry:
            continue
        if entry == '*':
            return True

        if host_ip is not None:
            try:
                if host_ip in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                pass

        entry = entry.lstrip('.')
        if (
            host == entry
            or host.endswith('.' + entry)
            or host_and_port == entry
            or host_and_port.endswith('.' + entry)
        ):
            return True

    return False


class RESTResponse(io.IOBase):

    def __init__(self, resp) -> None:
        self.response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = None

    def read(self):
        if self.data is None:
            self.data = self.response.data
        return self.data

    @property
    def headers(self):
        """Returns a dictionary of response headers."""
        return self.response.headers

    def getheaders(self):
        """Returns a dictionary of the response headers; use ``headers`` instead."""
        return self.response.headers

    def getheader(self, name, default=None):
        """Returns a given response header; use ``headers.get()`` instead."""
        return self.response.headers.get(name, default)


class RESTClientObject:

    def __init__(self, configuration) -> None:
        # urllib3.PoolManager will pass all kw parameters to connectionpool
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/poolmanager.py#L75  # noqa: E501
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/connectionpool.py#L680  # noqa: E501
        # Custom SSL certificates and client certificates: http://urllib3.readthedocs.io/en/latest/advanced-usage.html  # noqa: E501

        # cert_reqs
        if configuration.verify_ssl:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE

        pool_args = {
            "cert_reqs": cert_reqs,
            "ca_certs": configuration.ssl_ca_cert,
            "cert_file": configuration.cert_file,
            "key_file": configuration.key_file,
            "ca_cert_data": configuration.ca_cert_data,
        }
        if configuration.assert_hostname is not None:
            pool_args['assert_hostname'] = (
                configuration.assert_hostname
            )

        if configuration.retries is not None:
            pool_args['retries'] = configuration.retries

        if configuration.tls_server_name:
            pool_args['server_hostname'] = configuration.tls_server_name


        if configuration.socket_options is not None:
            pool_args['socket_options'] = configuration.socket_options

        if configuration.connection_pool_maxsize is not None:
            pool_args['maxsize'] = configuration.connection_pool_maxsize

        # https pool manager
        self.pool_manager: urllib3.PoolManager

        if configuration.proxy and not should_bypass_proxies(
            configuration.host, configuration.no_proxy or ''
        ):
            if is_socks_proxy_url(configuration.proxy):
                from urllib3.contrib.socks import SOCKSProxyManager
                pool_args["proxy_url"] = configuration.proxy
                pool_args["headers"] = configuration.proxy_headers
                self.pool_manager = SOCKSProxyManager(**pool_args)
            else:
                pool_args["proxy_url"] = configuration.proxy
                pool_args["proxy_headers"] = configuration.proxy_headers
                if configuration.proxy_ssl_context is not None:
                    pool_args["proxy_ssl_context"] = configuration.proxy_ssl_context
                self.pool_manager = urllib3.ProxyManager(**pool_args)
        else:
            self.pool_manager = urllib3.PoolManager(**pool_args)

    def request(
        self,
        method,
        url,
        headers=None,
        body=None,
        post_params=None,
        _request_timeout=None
    ):
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        method = method.upper()
        assert method in [
            'GET',
            'HEAD',
            'DELETE',
            'POST',
            'PUT',
            'PATCH',
            'OPTIONS'
        ]

        if post_params and body:
            raise ApiValueError(
                "body parameter cannot be used with post_params parameter."
            )

        post_params = post_params or {}
        headers = headers or {}

        timeout = None
        if _request_timeout:
            if isinstance(_request_timeout, (int, float)):
                timeout = urllib3.Timeout(total=_request_timeout)
            elif (
                    isinstance(_request_timeout, tuple)
                    and len(_request_timeout) == 2
                ):
                timeout = urllib3.Timeout(
                    connect=_request_timeout[0],
                    read=_request_timeout[1]
                )

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`
            if method in ['POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']:

                content_type = headers.get('Content-Type')
                is_json = (
                    not content_type
                    or contenttype_matches(content_type, 'application', 'json')
                )
                # JSON is valid YAML 1.2, so structured YAML bodies can use
                # the existing JSON serializer:
                # https://yaml.org/spec/1.2.2/#13-relation-to-json
                is_structured_yaml = (
                    content_type
                    and (
                        contenttype_matches(content_type, 'application', 'yaml')
                        or contenttype_matches(content_type, 'text', 'yaml')
                        or contenttype_matches(content_type, 'text', 'x-yaml')
                    )
                    and not isinstance(body, (str, bytes))
                )
                if is_json or is_structured_yaml:
                    request_body = None
                    if body is not None:
                        request_body = json.dumps(body)
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif contenttype_matches(content_type, 'application', 'x-www-form-urlencoded'):
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=False,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif contenttype_matches(content_type, 'multipart', 'form-data'):
                    # must del headers['Content-Type'], or the correct
                    # Content-Type which generated by urllib3 will be
                    # overwritten.
                    del headers['Content-Type']
                    # Ensures that dict objects are serialized
                    post_params = [(a, json.dumps(b)) if isinstance(b, dict) else (a,b) for a, b in post_params]
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=True,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                # Pass a `string` parameter directly in the body to support
                # other content types than JSON when `body` argument is
                # provided in serialized form.
                elif isinstance(body, str) or isinstance(body, bytes):
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif content_type.startswith('text/') and isinstance(body, bool):
                    request_body = "true" if body else "false"
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        preload_content=False,
                        timeout=timeout,
                        headers=headers)
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiException(status=0, reason=msg)
            # For `GET`, `HEAD`
            else:
                r = self.pool_manager.request(
                    method,
                    url,
                    fields={},
                    timeout=timeout,
                    headers=headers,
                    preload_content=False
                )
        except urllib3.exceptions.SSLError as e:
            msg = "\n".join([type(e).__name__, str(e)])
            raise ApiException(status=0, reason=msg)

        return RESTResponse(r)
