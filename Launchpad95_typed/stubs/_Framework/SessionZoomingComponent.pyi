"""Type stub for ``_Framework.SessionZoomingComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, List, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SessionComponent import SessionComponent


class SessionZoomingComponent(CompoundComponent):
    """Zoomed session view (matrix of clip states + scene bank buttons)."""

    def __init__(self, session: Optional[SessionComponent] = None,
                 enable_skinning: bool = False, *a: Any, **k: Any) -> None:
        ...

    def on_scene_list_changed(self) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def set_button_matrix(self, buttons: Optional[ButtonMatrixElement]) -> None:
        ...

    def set_nav_buttons(self, up: Optional[ButtonElement],
                        down: Optional[ButtonElement],
                        left: Optional[ButtonElement],
                        right: Optional[ButtonElement]) -> None:
        ...

    def set_nav_up_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_nav_down_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_nav_left_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_nav_right_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_scene_bank_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_empty_value(self, value: Any) -> None:
        ...

    def set_playing_value(self, value: Any) -> None:
        ...

    def set_stopped_value(self, value: Any) -> None:
        ...

    def set_selected_value(self, value: Any) -> None:
        ...

    def update(self) -> None:
        ...


class DeprecatedSessionZoomingComponent(SessionZoomingComponent):
    """The variant with a single zoom toggle button (pre-Live-9 API)."""

    def __init__(self, *a: Any, **k: Any) -> None:
        ...

    def set_button_matrix(self, buttons: Optional[ButtonMatrixElement]) -> None:
        ...

    def set_zoom_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def update(self) -> None:
        ...
