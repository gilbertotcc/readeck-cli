import json

from readeck_cli.cli.output import render_records


RECORDS = [
    {"title": "First bookmark", "url": "https://example.test/first"},
    {"title": "Second bookmark", "url": "https://example.test/second"},
]


def test_render_records_human_readable() -> None:
    output = render_records(RECORDS, as_json=False)

    assert output == (
        "title: First bookmark\n"
        "url: https://example.test/first\n"
        "\n"
        "title: Second bookmark\n"
        "url: https://example.test/second"
    )


def test_render_records_json() -> None:
    output = render_records(RECORDS, as_json=True)

    assert json.loads(output) == RECORDS


def test_render_records_empty_human_readable() -> None:
    assert render_records([], as_json=False) == ""


def test_render_records_empty_json() -> None:
    assert render_records([], as_json=True) == "[]"
