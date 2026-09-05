import httpx

from readeck_cli.infrastructure.readeck_client import PaginationInfo, PaginationParams


def test_pagination_params_omits_unset_fields() -> None:
    assert PaginationParams().to_query_params() == {}


def test_pagination_params_includes_zero_values() -> None:
    assert PaginationParams(limit=0, offset=0).to_query_params() == {"limit": 0, "offset": 0}


def test_pagination_params_includes_only_set_field() -> None:
    assert PaginationParams(limit=10).to_query_params() == {"limit": 10}
    assert PaginationParams(offset=20).to_query_params() == {"offset": 20}


def test_pagination_info_from_headers_parses_counts() -> None:
    headers = httpx.Headers({"Total-Count": "137", "Total-Pages": "7"})

    info = PaginationInfo.from_headers(headers)

    assert info.total_count == 137
    assert info.total_pages == 7


def test_pagination_info_from_headers_defaults_when_missing() -> None:
    info = PaginationInfo.from_headers(httpx.Headers({}))

    assert info.total_count == 0
    assert info.total_pages == 0


def test_pagination_info_from_headers_defaults_on_invalid_value() -> None:
    headers = httpx.Headers({"Total-Count": "not-a-number", "Total-Pages": "7"})

    info = PaginationInfo.from_headers(headers)

    assert info.total_count == 0
    assert info.total_pages == 7
