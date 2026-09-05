import click


@click.group(invoke_without_command=True)
@click.pass_context
def bookmarks_group(ctx: click.Context) -> None:
    """Manage Readeck bookmarks."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
