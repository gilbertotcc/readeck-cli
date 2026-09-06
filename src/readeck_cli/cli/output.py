import json
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def render_json(records: Sequence[Mapping[str, object]]) -> str:
    """Render a list of records as formatted JSON."""
    return json.dumps(list(records), indent=2)


def render_detail_block(title: str, fields: Sequence[tuple[str, str]]) -> str:
    """Render one record as a title line and an aligned "Label: value" block.

    Used for every human-readable record display (a single item, or one item
    among several), so that "get" and "list" style commands look consistent.
    """
    width = max(len(label) + 1 for label, _ in fields)
    lines = [title]
    lines.extend(f"  {(label + ':').ljust(width)} {value}" for label, value in fields)
    return "\n".join(lines)
