"""Type stub for ``_Framework.ModeSelectorComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


class ModeSelectorComponent(ControlSurfaceComponent):
    """A component with a set of modes selected by buttons."""

    def __init__(self, *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def set_mode_toggle(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_mode_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_mode(self, mode: int) -> None:
        ...

    def number_of_modes(self) -> int:
        ...

    def mode_index_has_listener(self, listener: Callable[..., Any]) -> bool:
        ...

    def add_mode_index_listener(self, listener: Callable[..., Any]) -> None:
        ...

    def remove_mode_index_listener(self, listener: Callable[..., Any]) -> None:
        ...
