import json
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def render_records(records: Sequence[Mapping[str, object]], *, as_json: bool) -> str:
    """Render a list of records as human-readable text or JSON.

    Human output is one block per record ("key: value" lines), separated by
    a blank line. JSON output is an array of objects with the same fields.
    """
    if as_json:
        return json.dumps(list(records), indent=2)
    return "\n\n".join("\n".join(f"{key}: {value}" for key, value in record.items()) for record in records)
