import os
from dataclasses import dataclass

import click


BASE_URL_ENV_VAR = "READECK_BASE_URL"
TOKEN_ENV_VAR = "READECK_BEARER_TOKEN"  # noqa: S105


@dataclass(frozen=True, slots=True)
class ReadeckCredentials:
    """Raw Readeck API credentials, as read from the environment."""

    base_url: str
    api_token: str


def load_credentials() -> ReadeckCredentials:
    """Read Readeck API credentials from the environment.

    Raises `click.UsageError` if a required variable is missing.
    """
    base_url = os.environ.get(BASE_URL_ENV_VAR, "").strip()
    api_token = os.environ.get(TOKEN_ENV_VAR, "").strip()

    missing = [name for name, value in ((BASE_URL_ENV_VAR, base_url), (TOKEN_ENV_VAR, api_token)) if not value]
    if missing:
        message = f"Missing required environment variable(s): {', '.join(missing)}"
        raise click.UsageError(message)

    return ReadeckCredentials(base_url=base_url, api_token=api_token)
