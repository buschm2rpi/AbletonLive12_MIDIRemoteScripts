"""Type stub for ``_Framework.ClipSlotComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from Live.Song import ClipSlot


class ClipSlotComponent(ControlSurfaceComponent):
    """A single clip slot in the session (launch/select/delete/duplicate)."""

    def __init__(self, *a: Any, **k: Any) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def set_clip_slot(self, clip_slot: Optional[ClipSlot]) -> None:
        ...

    def set_launch_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_delete_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_select_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_duplicate_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_triggered_to_play_value(self, value: Any) -> None:
        ...

    def set_triggered_to_record_value(self, value: Any) -> None:
        ...

    def set_started_value(self, value: Any) -> None:
        ...

    def set_recording_value(self, value: Any) -> None:
        ...

    def set_stopped_value(self, value: Any) -> None:
        ...

    def set_record_button_value(self, value: Any) -> None:
        ...

    def set_clip_palette(self, palette: Any) -> None:
        ...

    def set_clip_rgb_table(self, rgb_table: Any) -> None:
        ...

    def has_clip(self) -> bool:
        ...

    def update(self) -> None:
        ...
