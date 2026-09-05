import click

from readeck_cli.cli.output import render_records
from readeck_cli.commands import CommandError, get_highlights
from readeck_cli.config import load_credentials


@click.group(invoke_without_command=True)
@click.pass_context
def highlights_group(ctx: click.Context) -> None:
    """Manage Readeck highlights."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command(name="get")
@click.argument("bookmark_id")
@click.option("--json", "as_json", is_flag=True, help="Print raw JSON output.")
def get_command(bookmark_id: str, *, as_json: bool) -> None:
    """List a bookmark's highlights."""
    credentials = load_credentials()

    try:
        highlights = get_highlights(credentials, bookmark_id)
    except CommandError as exc:
        raise click.ClickException(str(exc)) from exc

    records = [
        {
            "id": highlight.id,
            "created": highlight.created,
            "color": highlight.color,
            "text": highlight.text,
            "note": highlight.note,
        }
        for highlight in highlights
    ]
    click.echo(render_records(records, as_json=as_json))


highlights_group.add_command(get_command)
