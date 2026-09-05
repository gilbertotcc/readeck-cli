import click

from readeck_cli.cli.info import info_command


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="readeck-cli")
@click.pass_context
def main(ctx: click.Context) -> None:
    """readeck-cli: a command line client for Readeck."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


main.add_command(info_command)


__all__ = ["main"]
