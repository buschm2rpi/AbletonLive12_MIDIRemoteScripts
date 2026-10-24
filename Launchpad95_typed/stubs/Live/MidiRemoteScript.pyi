"""Type stub for ``Live.MidiRemoteScript`` (type-checking only).

The host object Live passes to ``create_instance(c_instance)`` — the single
seam between the remote script and Live. This is the concrete type behind
the ``HostApi`` protocol in ``contracts.py``.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from Live.Application import Application
from Live.NoteRepeat import NoteRepeat
from Live.Song import Song
from Live.Track import Track


class MidiRemoteScript:
    """Ableton's remote-script host object (c_instance)."""

    def song(self) -> Song:
        ...

    def application(self) -> Application:
        ...

    def send_midi(self, midi_bytes: bytes) -> None:
        ...

    def show_message(self, message: str) -> None:
        ...

    def log_message(self, message: str) -> None:
        ...

    def request_rebuild_midi_map(self) -> None:
        ...

    def set_pad_translation(
        self,
        translations: List[Tuple[int, int, int, int, int]],
    ) -> None:
        """(msg_type, msg_identifier, msg_channel,
        translated_identifier, translated_channel) tuples."""
        ...

    def set_session_highlight(
        self,
        track_offset: int,
        scene_offset: int,
        width: int,
        height: int,
        include_return_tracks: bool,
    ) -> None:
        ...

    def toggle_lock(self) -> None:
        ...

    def update_locks(self) -> None:
        ...

    def set_feedback_channels(self, channels: List[int]) -> None:
        ...

    def set_feedback_velocity(self, velocity: int) -> None:
        ...

    def set_controlled_track(self, track: Optional[Track]) -> None:
        ...

    def release_controlled_track(self) -> None:
        ...

    def instance_identifier(self) -> int:
        ...

    def handle(self) -> int:
        ...

    @property
    def note_repeat(self) -> NoteRepeat:
        ...
