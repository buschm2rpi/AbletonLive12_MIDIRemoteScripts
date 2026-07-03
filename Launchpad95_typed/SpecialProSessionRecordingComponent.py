from __future__ import annotations
from typing import Any

# imported from https://github.com/poltow/Launchpad97

import Live
from _Framework.ClipCreator import ClipCreator
from _Framework.SessionRecordingComponent import SessionRecordingComponent

_Q = Live.Song.Quantization


class SpecialProSessionRecordingComponent(SessionRecordingComponent):
    def __init__(
        self, target_track_component: Any, control_surface: Any, *a: Any, **k: Any
    ) -> None:
        self._control_surface = control_surface
        self._target_track_component = target_track_component
        super(SpecialProSessionRecordingComponent, self).__init__(
            ClipCreator(), True, *a, **k
        )
        self._is_record_mode: bool = False

    def _set_parent(self, parent: Any) -> None:
        self._parent = parent

    def set_record_mode(self, record_mode: bool) -> None:
        self._is_record_mode = record_mode

    def _is_fixed_length_on(self) -> bool:
        return self._parent._is_fixed_length_on()

    def set_enabled(self, enable: bool) -> None:
        super(SpecialProSessionRecordingComponent, self).set_enabled(enable)

    def _get_fixed_length(self) -> Any:
        return self._parent._get_fixed_length()

    def _get_launch_quant(self) -> Any:
        return self._parent._get_launch_quant()

    def _on_record_button_value(self) -> None:
        if self.is_enabled():
            if self._is_record_mode:
                self._handle_pro_mode_record_behavior()
            else:
                if not self._stop_recording():
                    self._start_recording()
                    self._control_surface.show_message("SESSION RECORD ON")
                else:
                    self._control_surface.show_message("SESSION RECORD OFF")

    def _handle_pro_mode_record_behavior(self) -> None:
        track = self._target_track_component.target_track  # Selected Track
        status = self.song().session_record_status
        was_recording: bool = (
            status != Live.Song.SessionRecordStatus.off or self.song().session_record
        )
        if self._track_can_record(track) and not was_recording:
            if self._is_fixed_length_on():
                self.song().trigger_session_record(self._get_fixed_length())
            else:
                self.song().trigger_session_record()
        elif not self._stop_recording():
            self._start_recording()
            self._control_surface.show_message("SESSION RECORD ON")
        else:
            self._control_surface.show_message("SESSION RECORD OFF")

    def _track_can_record(self, track: Any) -> bool:
        return (
            track.can_be_armed
            and (track.arm or track.implicit_arm)
            and track in self.song().tracks
        )
