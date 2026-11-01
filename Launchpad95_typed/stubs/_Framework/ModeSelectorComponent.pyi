"""Type stub for ``_Framework.ModeSelectorComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence, Tuple

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


class ModeSelectorComponent(ControlSurfaceComponent):
    """A component with a set of modes selected by buttons."""

    # (mode, sender, observer) stack; see set_mode() / _mode_value() /
    # _clean_heap() in the real _Framework.
    _modes_heap: List[Tuple[int, Any, Any]]
    # The buttons driving the modes (set via set_mode_buttons()).
    _modes_buttons: List[ButtonElement]

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

    def _clean_heap(self) -> None:
        ...

    def _mode_value(self, value: int, sender: ButtonElement) -> None:
        ...

    def number_of_modes(self) -> int:
        ...

    def mode_index_has_listener(self, listener: Callable[..., Any]) -> bool:
        ...

    def add_mode_index_listener(self, listener: Callable[..., Any]) -> None:
        ...

    def remove_mode_index_listener(self, listener: Callable[..., Any]) -> None:
        ...
