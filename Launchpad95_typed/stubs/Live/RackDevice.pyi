"""Type stub for ``Live.RackDevice`` (type-checking only)."""
from __future__ import annotations

from Live.Device import Device, DeviceType


class RackDevice(Device):
    """A Live device rack (instrument rack / effect rack)."""

    def __init__(self, name: str = "Rack", type: int = DeviceType.instrument) -> None:
        ...
