from dataclasses import dataclass
from typing import TYPE_CHECKING

from readeck_cli.commands.errors import CommandError
from readeck_cli.infrastructure.readeck_client import ReadeckClient, ReadeckClientConfig, ReadeckClientError


if TYPE_CHECKING:
    import httpx

    from readeck_cli.config import ReadeckCredentials


@dataclass(frozen=True, slots=True)
class Highlight:
    """A single highlight (annotation) on a bookmark."""

    id: str
    created: str
    color: str
    text: str
    note: str


def get_highlights(
    credentials: ReadeckCredentials,
    bookmark_id: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> tuple[Highlight, ...]:
    """Fetch and parse a bookmark's highlights (annotations)."""
    try:
        config = ReadeckClientConfig.from_params(base_url=credentials.base_url, api_token=credentials.api_token)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc

    try:
        with ReadeckClient.from_config(config, transport=transport) as client:
            payload = client.get_highlights(bookmark_id)
    except ReadeckClientError as exc:
        raise CommandError(str(exc)) from exc

    return tuple(
        Highlight(
            id=item.get("id", ""),
            created=item.get("created", ""),
            color=item.get("color", ""),
            text=item.get("text", ""),
            note=item.get("note", ""),
        )
        for item in payload
    )
