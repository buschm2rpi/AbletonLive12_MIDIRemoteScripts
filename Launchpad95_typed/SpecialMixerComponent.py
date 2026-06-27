from __future__ import annotations
from typing import Any, Optional

from _Framework.MixerComponent import MixerComponent
from .DefChannelStripComponent import DefChannelStripComponent
from _Framework.ButtonElement import ButtonElement


class SpecialMixerComponent(MixerComponent):
    """Class encompassing several defaultable channel strips to form a mixer"""

    def __init__(self, num_tracks: int, num_returns: int = 0) -> None:
        self._osd: Any = None
        MixerComponent.__init__(self, num_tracks, num_returns)
        self._unarm_all_button: Optional[ButtonElement] = None
        self._unsolo_all_button: Optional[ButtonElement] = None
        self._unmute_all_button: Optional[ButtonElement] = None

    def disconnect(self) -> None:
        if self._unarm_all_button is not None:
            self._unarm_all_button.remove_value_listener(self._unarm_all_value)
            self._unarm_all_button = None
        if self._unsolo_all_button is not None:
            self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
            self._unsolo_all_button = None
        if self._unmute_all_button is not None:
            self._unmute_all_button.remove_value_listener(self._unmute_all_value)
            self._unmute_all_button = None
        MixerComponent.disconnect(self)

    def set_global_buttons(
        self,
        unarm_all: Optional[ButtonElement],
        unsolo_all: Optional[ButtonElement],
        unmute_all: Optional[ButtonElement],
    ) -> None:
        assert isinstance(unarm_all, (ButtonElement, type(None)))
        assert isinstance(unsolo_all, (ButtonElement, type(None)))
        assert isinstance(unmute_all, (ButtonElement, type(None)))
        if self._unarm_all_button is not None:
            self._unarm_all_button.remove_value_listener(self._unarm_all_value)
        self._unarm_all_button = unarm_all
        if self._unarm_all_button is not None:
            self._unarm_all_button.add_value_listener(self._unarm_all_value)
            self._unarm_all_button.turn_off()
        if self._unsolo_all_button is not None:
            self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
        self._unsolo_all_button = unsolo_all
        if self._unsolo_all_button is not None:
            self._unsolo_all_button.add_value_listener(self._unsolo_all_value)
            self._unsolo_all_button.turn_off()
        if self._unmute_all_button is not None:
            self._unmute_all_button.remove_value_listener(self._unmute_all_value)
        self._unmute_all_button = unmute_all
        if self._unmute_all_button is not None:
            self._unmute_all_button.add_value_listener(self._unmute_all_value)
            self._unmute_all_button.turn_off()

    def _reassign_tracks(self) -> None:
        MixerComponent._reassign_tracks(self)
        if self._is_enabled:
            self._update_OSD()

    def _create_strip(self) -> DefChannelStripComponent:
        return DefChannelStripComponent()

    def set_osd(self, osd: Any) -> None:
        self._osd = osd

    def update(self) -> None:
        MixerComponent.update(self)
        if self._is_enabled:
            self._update_OSD()

    def set_enabled(self, enabled: bool) -> None:
        MixerComponent.set_enabled(self, enabled)
        if enabled:
            self._update_OSD()

    def _update_OSD(self) -> None:
        if self._osd is not None:
            self._osd.mode = "Mixer"
            for i in range(8):
                self._osd.attribute_names[i] = " "
                self._osd.attributes[i] = " "

            tracks = self.tracks_to_use()
            idx: int = 0
            for i in range(len(tracks)):
                if idx < 8 and len(tracks) > i + self._track_offset:
                    track = tracks[i + self._track_offset]
                    if track is not None:
                        self._osd.attribute_names[idx] = str(track.name)
                    else:
                        self._osd.attribute_names[idx] = " "
                    self._osd.attributes[idx] = " "
                idx += 1

            self._osd.info[0] = " "
            self._osd.info[1] = " "
            self._osd.update()

    def _unarm_all_value(self, value: int) -> None:
        assert self._unarm_all_button is not None
        assert value in range(128)
        if self.is_enabled():
            if value != 0 or not self._unarm_all_button.is_momentary():
                for track in self.song().tracks:
                    if track.can_be_armed and track.arm:
                        track.arm = False

    def _unsolo_all_value(self, value: int) -> None:
        assert self._unsolo_all_button is not None
        assert value in range(128)
        if self.is_enabled():
            if value != 0 or not self._unsolo_all_button.is_momentary():
                for track in tuple(self.song().tracks) + tuple(
                    self.song().return_tracks
                ):
                    if track.solo:
                        track.solo = False

    def _unmute_all_value(self, value: int) -> None:
        assert self._unmute_all_button is not None
        assert value in range(128)
        if self.is_enabled():
            if value != 0 or not self._unmute_all_button.is_momentary():
                for track in tuple(self.song().tracks) + tuple(
                    self.song().return_tracks
                ):
                    if track.mute:
                        track.mute = False
