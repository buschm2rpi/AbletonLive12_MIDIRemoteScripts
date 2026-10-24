"""Type stub for ``Live.Base`` (type-checking only)."""
from __future__ import annotations


class LimitationError(Exception):
    """Raised by Live when a document limit is hit (e.g. too many scenes)."""


def log(message: str) -> None:
    """Write to Live's console log."""
    ...
