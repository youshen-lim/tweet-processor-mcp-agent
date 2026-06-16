"""
Optional source context helpers.

Source context is intended for public audience signals, objections, and
language patterns that can guide tweet framing without replacing the article as
the source of truth.
"""

from pathlib import Path
from typing import Optional


MAX_SOURCE_CONTEXT_CHARS = 6000


def load_optional_source_context(path_value: Optional[str]) -> str:
    """Load optional source context from a local file."""
    if path_value is None:
        return ""

    source_path = path_value.strip()
    if not source_path:
        return ""

    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(f"Source context file not found: {source_path}")
    if not path.is_file():
        raise ValueError(f"Source context path is not a file: {source_path}")

    with path.open(encoding="utf-8") as context_file:
        return context_file.read(MAX_SOURCE_CONTEXT_CHARS).strip()
