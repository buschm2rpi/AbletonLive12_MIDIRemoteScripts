"""Type stub for ``_Framework.ControlSurfaceComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, Optional

from _Framework.SubjectSlot import Subject
from _Framework.Task import TaskGroup
from Live.Song import Song


class ControlSurfaceComponent(Subject):
    """Base class of all control-surface components."""

    name: str
    canonical_parent: Any
    is_private: bool

    def __init__(self, name: str = "",
                 register_component: Optional[Callable[[Any], None]] = None,
                 song: Optional[Callable[[], Song]] = None,
                 layer: Any = None,
                 is_enabled: bool = True,
                 is_root: bool = False,
                 *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    @property
    def is_root(self) -> bool:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def update(self) -> None:
        ...

    def update_all(self) -> None:
        ...

    def set_enabled(self, enable: bool) -> None:
        ...

    def _set_enabled_recursive(self, enable: bool) -> None:
        ...

    def set_allow_update(self, allow_updates: bool) -> None:
        ...

    def control_notifications_enabled(self) -> bool:
        ...

    def application(self) -> Any:
        ...

    def song(self) -> Song:
        ...

    @property
    def _tasks(self) -> TaskGroup:
        ...

    def is_enabled(self, explicit: bool = False) -> bool:
        ...

    def on_track_list_changed(self) -> None:
        ...

    def on_scene_list_changed(self) -> None:
        ...

    def on_selected_track_changed(self) -> None:
        ...

    def on_selected_scene_changed(self) -> None:
        ...
