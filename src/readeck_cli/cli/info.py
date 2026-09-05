import json

import click

from readeck_cli.commands import CommandError, get_instance_info
from readeck_cli.config import load_credentials


@click.command(name="info")
@click.option("--json", "as_json", is_flag=True, help="Print raw JSON output.")
def info_command(*, as_json: bool) -> None:
    """Show information about the configured Readeck instance."""
    credentials = load_credentials()

    try:
        instance_info = get_instance_info(base_url=credentials.base_url, api_token=credentials.api_token)
    except CommandError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        payload = {
            "release": instance_info.release,
            "canonical": instance_info.canonical,
            "build": instance_info.build,
            "features": list(instance_info.features),
        }
        click.echo(json.dumps(payload, indent=2))
        return

    kind = f"nightly build {instance_info.build}" if instance_info.is_nightly else "stable"
    click.echo(f"Readeck {instance_info.canonical} ({kind})")
    click.echo(f"Features: {', '.join(instance_info.features) or 'none'}")
