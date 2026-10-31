"""Type stub for ``_Framework.ControlSurface`` (type-checking only).

The 567-line god-class base of every remote script. This stub declares the
surface ``Launchpad95_typed`` depends on (see the responsibility map in
``plan_control_surface_protocols.md`` §3). The listener methods for the
``received_midi`` / ``disconnect`` subject events are declared explicitly
(the real class gets them from the ``Subject`` metaclass).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Optional, Tuple

from _Framework.ControlElement import ControlElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SubjectSlot import SlotManager, Subject
from Live.Application import Application
from Live.Device import Device
from Live.MidiRemoteScript import MidiRemoteScript
from Live.Song import Song
from Live.Track import Track


class ControlSurface(Subject, SlotManager):
    """Base class of all Ableton remote-script control surfaces."""

    received_midi: tuple
    __subject_events__: tuple

    # The host object (Live.MidiRemoteScript) — the one seam to Live.
    # Private in the real class; declared here because the script's
    # ``host_api`` property reads it.
    _c_instance: MidiRemoteScript

    # Registered controls (a list; the base class reassigns it to None in
    # ``disconnect``, but the script only iterates it while connected).
    controls: List[ControlElement]

    def __init__(self, c_instance: Optional[MidiRemoteScript] = None,
                 *a: Any, **k: Any) -> None:
        ...

    # -- registry ----------------------------------------------------------
    @property
    def components(self) -> Tuple[ControlSurfaceComponent, ...]:
        ...

    @property
    def root_components(self) -> Tuple[ControlSurfaceComponent, ...]:
        ...

    def _register_control(self, control: ControlElement) -> None:
        ...

    def _register_component(self, component: ControlSurfaceComponent) -> None:
        ...

    def get_control_by_name(self, control_name: str) -> Optional[ControlElement]:
        ...

    # -- host bridge -------------------------------------------------------
    def application(self) -> Application:
        ...

    def song(self) -> Song:
        ...

    def show_message(self, message: str) -> None:
        ...

    def log_message(self, *message: Any) -> None:
        ...

    def instance_identifier(self) -> int:
        ...

    def request_rebuild_midi_map(self) -> None:
        ...

    def build_midi_map(self, midi_map_handle: int) -> None:
        ...

    def set_pad_translations(
        self,
        pad_translations: List[Tuple[int, int, int, int, int]],
    ) -> None:
        """(msg_type, msg_identifier, msg_channel,
        translated_identifier, translated_channel) tuples."""
        ...

    def supports_pad_translation(self) -> bool:
        ...

    def set_feedback_channels(self, channels: List[int]) -> None:
        ...

    def set_controlled_track(self, track: Optional[Track]) -> None:
        ...

    def release_controlled_track(self) -> None:
        ...

    def suggest_input_port(self) -> str:
        ...

    def suggest_output_port(self) -> str:
        ...

    def suggest_map_mode(self, cc_no: int, channel: int) -> int:
        ...

    def suggest_needs_takeover(self, cc_no: int, channel: int) -> bool:
        ...

    # -- MIDI receive ------------------------------------------------------
    # Live delivers incoming MIDI messages as tuples of ints (see the
    # reconstructed fake ``handle_sysex`` and the per-model challenge
    # comparisons, e.g. ``midi_bytes[:7] == (240, 0, 32, 41, ...)``).
    def receive_midi(self, midi_bytes: tuple[int, ...]) -> None:
        ...

    def is_sysex_message(self, midi_bytes: tuple[int, ...]) -> bool:
        ...

    def handle_nonsysex(self, midi_bytes: tuple[int, ...]) -> None:
        ...

    def handle_sysex(self, midi_bytes: tuple[int, ...]) -> None:
        ...

    # -- MIDI send ---------------------------------------------------------
    def _send_midi(self, midi_event_bytes: tuple[int, ...],
                   optimized: Optional[bool] = True) -> bool:
        ...

    def _translate_message(self, msg_type: int, msg_identifier: int,
                           msg_channel: int, translated_identifier: int,
                           translated_channel: int) -> None:
        ...

    # -- lifecycle ---------------------------------------------------------
    def disconnect(self) -> None:
        ...

    def refresh_state(self) -> None:
        ...

    def update(self) -> None:
        ...

    def update_display(self) -> None:
        ...

    def set_enabled(self, enable: bool) -> None:
        ...

    def port_settings_changed(self) -> None:
        ...

    # -- tasks -------------------------------------------------------------
    def schedule_message(self, delay_in_ticks: int, callback: Callable[..., Any],
                         parameter: Any = None) -> None:
        ...

    # -- device locks ------------------------------------------------------
    def can_lock_to_devices(self) -> bool:
        ...

    def lock_to_device(self, device: Device) -> None:
        ...

    def unlock_from_device(self, device: Device) -> None:
        ...

    def restore_bank(self, bank_index: int) -> None:
        ...

    def set_device_component(self, device_component: Optional[DeviceComponent]) -> None:
        ...

    def toggle_lock(self) -> None:
        ...

    # -- session highlighting ----------------------------------------------
    def set_highlighting_session_component(
        self, session_component: Optional[SessionComponent]) -> None:
        ...

    def highlighting_session_component(self) -> Optional[SessionComponent]:
        ...

    def _set_session_highlight(self, track_offset: int, scene_offset: int,
                               width: int, height: int,
                               include_return_tracks: bool) -> None:
        ...

    # -- re-entrancy / suppression guards -----------------------------------
    @contextmanager
    def component_guard(self) -> Iterator[None]:
        ...

    @property
    def in_component_guard(self) -> bool:
        ...

    @contextmanager
    def accumulating_midi_messages(self) -> Iterator[None]:
        ...

    @contextmanager
    def suppressing_rebuild_requests(self) -> Iterator[None]:
        ...

    # -- subject events ------------------------------------------------------
    def notify_received_midi(self, *a: Any, **k: Any) -> None:
        ...

    def received_midi_has_listener(self, listener: Callable[..., Any]) -> bool:
        ...

    def add_received_midi_listener(self, listener: Callable[..., Any]) -> None:
        ...

    def remove_received_midi_listener(self, listener: Callable[..., Any]) -> None:
        ...

    def notify_disconnect(self, *a: Any, **k: Any) -> None:
        ...
