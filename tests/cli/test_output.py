import json

from readeck_cli.cli.output import render_detail_block, render_json


RECORDS = [
    {"title": "First bookmark", "url": "https://example.test/first"},
    {"title": "Second bookmark", "url": "https://example.test/second"},
]


def test_render_json() -> None:
    output = render_json(RECORDS)

    assert json.loads(output) == RECORDS


def test_render_json_empty() -> None:
    assert render_json([]) == "[]"


def test_render_detail_block_aligns_fields() -> None:
    output = render_detail_block("Title", [("ID", "abc123"), ("Description", "A short one")])

    assert output == ("Title\n  ID:          abc123\n  Description: A short one")


def test_render_detail_block_omits_empty_sections() -> None:
    output = render_detail_block("Title", [("ID", "abc123")], sections=[("Links", [])])

    assert "Links:" not in output


def test_render_detail_block_renders_non_empty_sections() -> None:
    output = render_detail_block("Title", [("ID", "abc123")], sections=[("Links", ["Related: https://x.test"])])

    assert output == ("Title\n  ID: abc123\n\n  Links:\n    - Related: https://x.test")
