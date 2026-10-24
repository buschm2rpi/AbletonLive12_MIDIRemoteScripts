"""Type stub for ``_Framework.EncoderElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional

from _Framework.InputControlElement import InputControlElement


class EncoderElement(InputControlElement):
    """A relative (encoder/CC) control element."""

    def __init__(self, msg_type: int, channel: int, identifier: int,
                 map_mode: int, encoder_sensitivity: Optional[float] = None,
                 *a: Any, **k: Any) -> None:
        ...

    def message_map_mode(self) -> int:
        ...

    def relative_value_to_delta(self, value: int) -> int:
        ...

    def normalize_value(self, value: int) -> float:
        ...

    def notify_value(self, value: int) -> None:
        ...
