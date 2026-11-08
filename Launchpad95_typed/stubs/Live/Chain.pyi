"""Type stub for ``Live.Chain`` (type-checking only).

Chains double as drum pads in Drum Rack devices; ``note`` is the pad's
MIDI note (present on drum-pad chains).
"""
from __future__ import annotations

from typing import Callable, List

from Live.Device import Device
from Live.Track import Track


class Chain:
    """A Live chain (rack chain / drum pad)."""

    canonical_parent: Track | Device | Chain

    @property
    def name(self) -> str:
        ...

    @property
    def note(self) -> int:
        ...

    @note.setter
    def note(self, value: int) -> None:
        ...

    @property
    def devices(self) -> List[Device]:
        ...

    @devices.setter
    def devices(self, value: List[Device]) -> None:
        ...

    @property
    def chains(self) -> List["Chain"]:
        ...

    def add_devices_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_devices_listener(self, callback: Callable[..., None]) -> None: ...
    def devices_has_listener(self, callback: Callable[..., None]) -> bool: ...
