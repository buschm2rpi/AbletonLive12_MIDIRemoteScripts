"""Type stub for ``_Framework.SliderElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any

from _Framework.EncoderElement import EncoderElement


class SliderElement(EncoderElement):
    """An absolute slider (CC) control element."""

    def __init__(self, msg_type: int, channel: int, identifier: int,
                 *a: Any, **k: Any) -> None:
        ...
