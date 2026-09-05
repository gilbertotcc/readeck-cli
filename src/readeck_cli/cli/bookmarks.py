import click

from readeck_cli.cli.output import render_records
from readeck_cli.commands import CommandError, get_bookmark, get_share_link
from readeck_cli.config import load_credentials


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

    click.echo(render_records([record], as_json=as_json))
