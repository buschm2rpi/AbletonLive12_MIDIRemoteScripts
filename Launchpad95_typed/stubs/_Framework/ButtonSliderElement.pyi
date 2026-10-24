"""Type stub for ``_Framework.ButtonSliderElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List

from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import SlotManager


class ButtonSliderElement(SliderElement, SlotManager):
    """A slider emulated by a row of buttons (no MIDI message of its own)."""

    _last_sent_value: int

    def __init__(self, buttons: List[ButtonElement]) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def message_channel(self) -> int:
        ...

    def message_identifier(self) -> int:
        ...

    def message_map_mode(self) -> int:
        ...

    def install_connections(self, install_translation_callback: Callable[..., Any],
                            install_mapping_callback: Callable[..., Any],
                            install_forwarding_callback: Callable[..., Any]) -> None:
        ...

    def connect_to(self, parameter: Any) -> None:
        ...

    def release_parameter(self) -> None:
        ...

    def identifier_bytes(self) -> Any:
        ...

    # Deliberately narrower than InputControlElement.send_value (no
    # force/channel): a button slider has no MIDI message of its own.
    def send_value(self, value: int) -> None:  # type: ignore[override]
        ...
