from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class ReadeckClientConfig:
    """Configuration for `ReadeckClient`."""

    base_url: str
    api_token: str
    timeout: float = 10.0  # seconds

    @classmethod
    def from_params(cls, *, base_url: str, api_token: str, timeout: float = 10.0) -> Self:
        if not base_url.strip():
            raise ValueError("base_url must not be empty")
        if not api_token.strip():
            raise ValueError("api_token must not be empty")
        return cls(base_url=base_url.rstrip("/"), api_token=api_token, timeout=timeout)
