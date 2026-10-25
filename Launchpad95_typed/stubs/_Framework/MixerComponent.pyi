"""Type stub for ``_Framework.MixerComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, List, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlElement import ControlElement
from Live.Track import Track


class MixerComponent(CompoundComponent):
    """Mixer view: channel strips, volume/pan/send controls, banking."""

    def __init__(self, num_tracks: int = 0, num_returns: int = 0,
                 auto_name: bool = False, invert_mute_feedback: bool = False,
                 *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def on_send_index_changed(self) -> None:
        ...

    @property
    def num_sends(self) -> int:
        ...

    def channel_strip(self, index: int) -> "ChannelStripComponent":
        ...

    def return_strip(self, index: int) -> "ChannelStripComponent":
        ...

    def master_strip(self) -> "ChannelStripComponent":
        ...

    def selected_strip(self) -> "ChannelStripComponent":
        ...

    def set_prehear_volume_control(self, control: Optional[ControlElement]) -> None:
        ...

    def set_crossfader_control(self, control: Optional[ControlElement]) -> None:
        ...

    def set_volume_controls(self, controls: Optional[Sequence[ControlElement]]) -> None:
        ...

    def set_pan_controls(self, controls: Optional[Sequence[ControlElement]]) -> None:
        ...

    def set_send_controls(self, controls: Optional[Sequence[ControlElement]]) -> None:
        ...

    def set_arm_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_solo_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_mute_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_track_select_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_shift_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_bank_buttons(self, up_button: Optional[ButtonElement],
                         down_button: Optional[ButtonElement]) -> None:
        ...

    def set_select_buttons(self, next_button: Optional[ButtonElement],
                           prev_button: Optional[ButtonElement]) -> None:
        ...

    def set_track_offset(self, new_offset: int) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def on_track_list_changed(self) -> None:
        ...

    def on_selected_track_changed(self) -> None:
        ...

    def on_num_sends_changed(self) -> None:
        ...

    def tracks_to_use(self) -> List[Track]:
        ...

    def update(self) -> None:
        ...
