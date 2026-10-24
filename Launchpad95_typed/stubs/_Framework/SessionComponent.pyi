"""Type stub for ``_Framework.SessionComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.CompoundComponent import CompoundComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.SceneComponent import SceneComponent
from Live.Scene import Scene
from Live.Track import Track


class SessionComponent(CompoundComponent):
    """The session view (clip launch grid, bank scrolling, ...)."""

    def __init__(self, num_tracks: int = 0, num_scenes: int = 0,
                 auto_name: bool = False, enable_skinning: bool = False,
                 *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def set_highlighting_callback(self, callback: Optional[Callable[..., Any]]) -> None:
        ...

    def scene(self, index: int) -> "SceneComponent":
        ...

    def selected_scene(self) -> Optional["SceneComponent"]:
        ...

    def set_scene_bank_buttons(self, down_button: Optional[ButtonElement],
                               up_button: Optional[ButtonElement]) -> None:
        ...

    def set_scene_bank_up_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_scene_bank_down_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_track_bank_buttons(self, right_button: Optional[ButtonElement],
                               left_button: Optional[ButtonElement]) -> None:
        ...

    def set_track_bank_left_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_track_bank_right_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_page_up_button(self, page_up_button: Optional[ButtonElement]) -> None:
        ...

    def set_page_down_button(self, page_down_button: Optional[ButtonElement]) -> None:
        ...

    def set_page_left_button(self, page_left_button: Optional[ButtonElement]) -> None:
        ...

    def set_page_right_button(self, page_right_button: Optional[ButtonElement]) -> None:
        ...

    def set_stop_all_clips_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_stop_track_clip_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_stop_clip_triggered_value(self, value: Any) -> None:
        ...

    def set_stop_clip_value(self, value: Any) -> None:
        ...

    def set_select_buttons(self, next_button: Optional[ButtonElement],
                           prev_button: Optional[ButtonElement]) -> None:
        ...

    def set_select_next_button(self, next_button: Optional[ButtonElement]) -> None:
        ...

    def set_select_prev_button(self, prev_button: Optional[ButtonElement]) -> None:
        ...

    def set_clip_launch_buttons(self, buttons: Optional[ButtonMatrixElement]) -> None:
        ...

    def set_scene_launch_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_mixer(self, mixer: Optional[MixerComponent]) -> None:
        ...

    def set_offsets(self, track_offset: int, scene_offset: int) -> None:
        ...

    def set_show_highlight(self, show_highlight: bool) -> None:
        ...

    def set_rgb_mode(self, color_palette: Any, color_table: Any,
                     clip_slots_only: bool = False) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def update(self) -> None:
        ...

    def on_scene_list_changed(self) -> None:
        ...

    def on_track_list_changed(self) -> None:
        ...

    def on_selected_scene_changed(self) -> None:
        ...

    def width(self) -> int:
        ...

    def height(self) -> int:
        ...

    def track_offset(self) -> int:
        ...

    def scene_offset(self) -> int:
        ...

    def tracks_to_use(self) -> List[Track]:
        ...

    @property
    def current_tracks(self) -> List[Track]:
        ...
