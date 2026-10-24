"""Type stub for ``_Framework.ChannelStripComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlElement import ControlElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from Live.Track import Track


class ChannelStripComponent(ControlSurfaceComponent):
    """One channel strip: volume/pan/sends, arm/solo/mute, selection."""

    def __init__(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def set_track(self, track: Optional[Track]) -> None:
        ...

    def reset_button_on_exchange(self, button: ButtonElement) -> None:
        ...

    def set_send_controls(self, controls: Optional[Sequence[ControlElement]]) -> None:
        ...

    def set_pan_control(self, control: Optional[ControlElement]) -> None:
        ...

    def set_volume_control(self, control: Optional[ControlElement]) -> None:
        ...

    def set_select_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_mute_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_solo_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_arm_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_shift_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_crossfade_toggle(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_invert_mute_feedback(self, invert_feedback: bool) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def on_selected_track_changed(self) -> None:
        ...

    def solo_button_pressed(self) -> bool:
        ...

    def arm_button_pressed(self) -> bool:
        ...

    def track_name_data_source(self) -> Any:
        ...

    @property
    def track(self) -> Optional[Track]:
        ...

    def update_solo_state(self, solo_exclusive: bool, new_value: bool,
                          respect_multi_selection: bool, track: Track) -> None:
        ...

    def update(self) -> None:
        ...
