"""Type stub for ``_Framework.ClipCreator`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional

from Live.Song import ClipSlot


class ClipCreator:
    """Creates clips in slots (used by the session recording component)."""

    grid_quantization: Any
    is_grid_triplet: bool
    fixed_length: int

    def create(self, slot: ClipSlot, length: Optional[int] = None) -> None:
        ...
