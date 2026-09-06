from typing import TYPE_CHECKING

import click

from readeck_cli.cli.output import render_detail_block, render_json
from readeck_cli.commands import CommandError, get_bookmark, get_share_link, list_bookmarks
from readeck_cli.config import load_credentials


if TYPE_CHECKING:
    from readeck_cli.commands import Bookmark, BookmarkDetails, PaginationInfo


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
        click.echo(render_json([record]))
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
        click.echo(render_json([record]))
        return

    click.echo(_format_bookmark(bookmark))


def _bookmark_fields(bookmark: Bookmark | BookmarkDetails) -> list[tuple[str, str]]:
    """Fields shared by "list" and "get" style bookmark records, so both look consistent."""
    return [
        ("ID", bookmark.id),
        ("URL", bookmark.url),
        ("Site", bookmark.site),
        ("Authors", ", ".join(bookmark.authors) or "none"),
        ("Labels", ", ".join(bookmark.labels) or "none"),
        ("Description", bookmark.description),
        ("Note", bookmark.note),
    ]


def _format_bookmark(bookmark: BookmarkDetails) -> str:
    """Render a bookmark's details as a labeled block, with links as a sub-list."""
    links = [f"{link.title}: {link.url}" for link in bookmark.links]
    return render_detail_block(bookmark.title or bookmark.id, _bookmark_fields(bookmark), sections=[("Links", links)])


@bookmarks_group.command(name="list")
@click.argument("search", required=False)
@click.option("--limit", type=int, default=None, help="Number of items per page.")
@click.option("--offset", type=int, default=None, help="Pagination offset.")
@click.option("--json", "as_json", is_flag=True, help="Print raw JSON output.")
def list_command(*, search: str | None, limit: int | None, offset: int | None, as_json: bool) -> None:
    """List bookmarks, optionally filtered by SEARCH."""
    credentials = load_credentials()

    try:
        bookmarks, pagination_info = list_bookmarks(credentials, search=search, limit=limit, offset=offset)
    except CommandError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(render_json([_to_record(bookmark) for bookmark in bookmarks]))
    elif bookmarks:
        click.echo("\n\n".join(_format_bookmark_summary(bookmark) for bookmark in bookmarks))
    else:
        click.echo("No bookmarks found.")

    _echo_pagination_summary(bookmarks, pagination_info)


def _format_bookmark_summary(bookmark: Bookmark) -> str:
    """Render one bookmark from a list, in the same style as "bookmarks get"."""
    return render_detail_block(bookmark.title or bookmark.id, _bookmark_fields(bookmark))


def _to_record(bookmark: Bookmark) -> dict[str, object]:
    return {
        "id": bookmark.id,
        "href": bookmark.href,
        "url": bookmark.url,
        "title": bookmark.title,
        "site": bookmark.site,
        "authors": list(bookmark.authors),
        "description": bookmark.description,
        "note": bookmark.note,
        "labels": list(bookmark.labels),
    }


def _echo_pagination_summary(bookmarks: list[Bookmark], pagination_info: PaginationInfo) -> None:
    if pagination_info.total_pages <= 1:
        return
    summary = f"{len(bookmarks)} of {pagination_info.total_count} across {pagination_info.total_pages} page(s)"
    click.echo(summary, err=True)
