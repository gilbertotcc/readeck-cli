from dataclasses import dataclass
from typing import TYPE_CHECKING

from readeck_cli.commands.errors import CommandError
from readeck_cli.infrastructure.readeck_client import ReadeckClient, ReadeckClientConfig, ReadeckClientError


if TYPE_CHECKING:
    import httpx

    from readeck_cli.config import ReadeckCredentials


@dataclass(frozen=True, slots=True)
class ShareLink:
    """A public share link for a bookmark."""

    url: str
    expires: str
    title: str
    id: str


def get_share_link(
    credentials: ReadeckCredentials,
    bookmark_id: str,
    *,
    with_notes: bool = False,
    transport: httpx.BaseTransport | None = None,
) -> ShareLink:
    """Fetch and parse a public share link for a bookmark."""
    try:
        config = ReadeckClientConfig.from_params(base_url=credentials.base_url, api_token=credentials.api_token)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc

    try:
        with ReadeckClient.from_config(config, transport=transport) as client:
            payload = client.get_share_link(bookmark_id, with_notes=with_notes)
    except ReadeckClientError as exc:
        raise CommandError(str(exc)) from exc

    return ShareLink(
        url=payload.get("url", ""),
        expires=payload.get("expires", ""),
        title=payload.get("title", ""),
        id=payload.get("id", ""),
    )


@dataclass(frozen=True, slots=True)
class BookmarkLink:
    """A single link collected from a bookmark's article."""

    title: str
    url: str


@dataclass(frozen=True, slots=True)
class BookmarkDetails:
    """A single bookmark's full details."""

    id: str
    href: str
    url: str
    title: str
    site: str
    authors: tuple[str, ...]
    description: str
    note: str
    labels: tuple[str, ...]
    links: tuple[BookmarkLink, ...]


def get_bookmark(
    bookmark_id: str,
    credentials: ReadeckCredentials,
    *,
    transport: httpx.BaseTransport | None = None,
) -> BookmarkDetails:
    """Fetch and parse a single bookmark's full details."""
    try:
        config = ReadeckClientConfig.from_params(base_url=credentials.base_url, api_token=credentials.api_token)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc

    try:
        with ReadeckClient.from_config(config, transport=transport) as client:
            payload = client.get_bookmark(bookmark_id)
    except ReadeckClientError as exc:
        raise CommandError(_error_message(exc)) from exc

    return BookmarkDetails(
        id=payload.get("id", ""),
        href=payload.get("href", ""),
        url=payload.get("url", ""),
        title=payload.get("title", ""),
        site=payload.get("site", ""),
        authors=tuple(payload.get("authors", [])),
        description=payload.get("description", ""),
        note=payload.get("note", ""),
        labels=tuple(payload.get("labels", [])),
        links=tuple(
            BookmarkLink(title=link.get("title", ""), url=link.get("url", "")) for link in payload.get("links", [])
        ),
    )


def _error_message(exc: ReadeckClientError) -> str:
    """Prefer the API's own error message over the generic transport one."""
    body = exc.response_json()
    message = body.get("message") if isinstance(body, dict) else None
    if isinstance(message, str) and message:
        return message
    return str(exc)
