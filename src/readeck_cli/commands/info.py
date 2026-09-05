from dataclasses import dataclass
from typing import TYPE_CHECKING

from readeck_cli.commands.errors import CommandError
from readeck_cli.infrastructure.readeck_client import ReadeckClient, ReadeckClientConfig, ReadeckClientError


if TYPE_CHECKING:
    import httpx

    from readeck_cli.config import ReadeckCredentials


@dataclass(frozen=True, slots=True)
class InstanceInfo:
    """Public information about a Readeck instance."""

    release: str
    canonical: str
    build: str
    features: tuple[str, ...]

    @property
    def is_nightly(self) -> bool:
        return bool(self.build)


def get_instance_info(
    credentials: ReadeckCredentials,
    *,
    transport: httpx.BaseTransport | None = None,
) -> InstanceInfo:
    """Fetch and parse public information about a Readeck instance."""
    try:
        config = ReadeckClientConfig.from_params(base_url=credentials.base_url, api_token=credentials.api_token)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc

    try:
        with ReadeckClient.from_config(config, transport=transport) as client:
            payload = client.get_info()
    except ReadeckClientError as exc:
        raise CommandError(str(exc)) from exc

    version = payload.get("version", {})
    return InstanceInfo(
        release=version.get("release", ""),
        canonical=version.get("canonical", ""),
        build=version.get("build", ""),
        features=tuple(payload.get("features", [])),
    )
