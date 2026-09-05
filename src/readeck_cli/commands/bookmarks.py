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
