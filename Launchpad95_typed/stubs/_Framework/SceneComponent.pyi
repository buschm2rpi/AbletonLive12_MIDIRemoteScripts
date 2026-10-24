"""Type stub for ``_Framework.SceneComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.CompoundComponent import CompoundComponent
from Live.Scene import Scene


class SceneComponent(CompoundComponent):
    """A single scene in the session (launch/select/delete buttons)."""

    def __init__(self, num_slots: int = 0,
                 tracks_to_use_callback: Optional[Callable[[], Any]] = None,
                 *a: Any, **k: Any) -> None:
        ...

    def on_track_list_changed(self) -> None:
        ...

    def set_scene(self, scene: Optional[Scene]) -> None:
        ...

    def set_launch_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_select_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_delete_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_track_offset(self, offset: int) -> None:
        ...

    def set_triggered_value(self, value: Any) -> None:
        ...

    def set_scene_value(self, value: Any) -> None:
        ...

    def set_no_scene_value(self, value: Any) -> None:
        ...

    def set_color_palette(self, palette: Any) -> None:
        ...

    def set_color_table(self, table: Any) -> None:
        ...

    def clip_slot(self, index: int) -> ClipSlotComponent:
        ...

    def update(self) -> None:
        ...
