from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    import httpx


class ReadeckClientError(Exception):
    """A single error type for every way a Readeck API call can fail.

    For transport-level failures (connection errors, timeouts, ...), chain
    the original exception with `raise ... from exc` so it remains
    available as `__cause__`.
    """

    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.request = request
        self.response = response

    @property
    def status_code(self) -> int | None:
        return self.response.status_code if self.response is not None else None

    def response_json(self) -> Any:
        if self.response is None:
            return None
        try:
            return self.response.json()
        except ValueError:
            return None
