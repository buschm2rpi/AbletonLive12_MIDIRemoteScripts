"""Type stub for ``Live.Scene`` (type-checking only)."""
from __future__ import annotations

from typing import Callable, List

from Live.Song import ClipSlot


class Scene:
    """A Live scene."""

    canonical_parent: object

    @property
    def name(self) -> str:
        ...

    @name.setter
    def name(self, value: str) -> None:
        ...

    @property
    def is_triggered(self) -> bool:
        ...

    @is_triggered.setter
    def is_triggered(self, value: bool) -> None:
        ...

    @property
    def color(self) -> int:
        ...

    @color.setter
    def color(self, value: int) -> None:
        ...

    @property
    def clip_slots(self) -> List[ClipSlot]:
        ...

    @clip_slots.setter
    def clip_slots(self, value: List[ClipSlot]) -> None:
        ...

    @property
    def is_empty(self) -> bool:
        ...

    def clip_slot(self, index: int) -> ClipSlot:
        ...

    def fire(self) -> None:
        ...

    def set_fire_button_state(self, state: bool) -> None:
        ...

    def _set_parent(self, parent: object) -> None:
        ...

    # -- subject listeners -------------------------------------------------
    def add_is_triggered_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_is_triggered_listener(self, callback: Callable[..., None]) -> None: ...
    def is_triggered_has_listener(self, callback: Callable[..., None]) -> bool: ...
    def add_color_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_color_listener(self, callback: Callable[..., None]) -> None: ...
    def color_has_listener(self, callback: Callable[..., None]) -> bool: ...
