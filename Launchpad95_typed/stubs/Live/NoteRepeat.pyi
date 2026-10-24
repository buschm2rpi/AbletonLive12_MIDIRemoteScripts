"""Type stub for ``Live.NoteRepeat`` (type-checking only).

The note-repeat object handed to the script via
``c_instance.note_repeat`` (a property on the host object). The script
drives it both through properties (``repeat_rate``, ``enabled``) and
methods (``set_enabled``, ``is_enabled``, ``set_freq_index``,
``freq_name``).
"""
from __future__ import annotations


class NoteRepeat:
    """Live's note-repeat engine."""

    @property
    def repeat_rate(self) -> float:
        ...

    @repeat_rate.setter
    def repeat_rate(self, value: float) -> None:
        ...

    @property
    def enabled(self) -> bool:
        ...

    @enabled.setter
    def enabled(self, value: bool) -> None:
        ...

    def set_enabled(self, enabled: bool) -> None:
        ...

    def is_enabled(self) -> bool:
        ...

    def set_freq_index(self, index: int) -> None:
        ...

    def freq_name(self) -> str:
        ...
