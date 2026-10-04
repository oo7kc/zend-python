from urllib.parse import quote


def path_segment(value: str) -> str:
    """Percent-encode one opaque URL path segment."""
    return quote(value, safe="")
