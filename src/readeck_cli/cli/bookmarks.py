from typing import TYPE_CHECKING

import click

from readeck_cli.cli.output import render_records
from readeck_cli.commands import CommandError, get_bookmark, get_share_link
from readeck_cli.config import load_credentials


if TYPE_CHECKING:
    from readeck_cli.commands import BookmarkDetails


@click.group(invoke_without_command=True)
@click.pass_context
def bookmarks_group(ctx: click.Context) -> None:
    """Manage Readeck bookmarks."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@bookmarks_group.command(name="share")
@click.argument("bookmark_id")
@click.option("--with-notes", is_flag=True, help="Include annotations and notes in the shared link.")
@click.option("--json", "as_json", is_flag=True, help="Print raw JSON output.")
def share_command(bookmark_id: str, *, with_notes: bool, as_json: bool) -> None:
    """Create a public share link for BOOKMARK_ID."""
    credentials = load_credentials()

    try:
        share_link = get_share_link(credentials, bookmark_id, with_notes=with_notes)
    except CommandError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        record = {
            "url": share_link.url,
            "expires": share_link.expires,
            "title": share_link.title,
            "id": share_link.id,
        }
        click.echo(render_records([record], as_json=True))
        return

    click.echo(f"Link: {share_link.url} (expires: {share_link.expires})")


@bookmarks_group.command(name="get")
@click.argument("bookmark_id")
@click.option("--json", "as_json", is_flag=True, help="Print raw JSON output.")
def bookmarks_get_command(bookmark_id: str, *, as_json: bool) -> None:
    """Show a single bookmark's full details."""
    credentials = load_credentials()

    try:
        bookmark = get_bookmark(bookmark_id, credentials)
    except CommandError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        record = {
            "id": bookmark.id,
            "href": bookmark.href,
            "url": bookmark.url,
            "title": bookmark.title,
            "site": bookmark.site,
            "authors": list(bookmark.authors),
            "description": bookmark.description,
            "note": bookmark.note,
            "labels": list(bookmark.labels),
            "links": [{"title": link.title, "url": link.url} for link in bookmark.links],
        }
        click.echo(render_records([record], as_json=True))
        return

    click.echo(_format_bookmark(bookmark))


def _format_bookmark(bookmark: BookmarkDetails) -> str:
    """Render a bookmark's details as a labeled block, with links as a sub-list."""
    fields = [
        ("ID", bookmark.id),
        ("URL", bookmark.url),
        ("Site", bookmark.site),
        ("Authors", ", ".join(bookmark.authors) or "none"),
        ("Labels", ", ".join(bookmark.labels) or "none"),
        ("Description", bookmark.description),
        ("Note", bookmark.note),
    ]
    width = max(len(label) + 1 for label, _ in fields)

    lines = [bookmark.title or bookmark.id]
    lines.extend(f"  {(label + ':').ljust(width)} {value}" for label, value in fields)

    if bookmark.links:
        lines.append("")
        lines.append("  Links:")
        lines.extend(f"    - {link.title}: {link.url}" for link in bookmark.links)

    return "\n".join(lines)
