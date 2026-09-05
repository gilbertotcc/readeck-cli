from dataclasses import dataclass
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    import httpx


@dataclass(frozen=True, slots=True)
class PaginationParams:
    """Request-side paging parameters for a `GET /bookmarks`-style endpoint."""

    limit: int | None = None
    offset: int | None = None

    def to_query_params(self) -> dict[str, int]:
        """Build a query-param dict, omitting unset fields.

        Uses `is not None` rather than truthiness: `limit=0`/`offset=0` are
        valid values that must reach the request.
        """
        params: dict[str, int] = {}
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        return params


@dataclass(frozen=True, slots=True)
class PaginationInfo:
    """Response-side pagination metadata, parsed from response headers."""

    total_count: int
    total_pages: int

    @classmethod
    def from_headers(cls, headers: httpx.Headers) -> Self:
        """Parse `Total-Count`/`Total-Pages`, defaulting to 0 if absent or invalid."""
        return cls(
            total_count=_parse_int(headers.get("Total-Count")),
            total_pages=_parse_int(headers.get("Total-Pages")),
        )


def _parse_int(value: str | None) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0
