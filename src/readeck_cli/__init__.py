import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="readeck-cli")
@click.pass_context
def main(ctx: click.Context) -> None:
    """readeck-cli: a command line client for Readeck."""
    click.echo(ctx.get_help())
