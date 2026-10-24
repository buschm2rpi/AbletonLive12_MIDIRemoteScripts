"""Type stub for ``_Framework.ButtonElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional

from _Framework.InputControlElement import InputControlElement
from _Framework.Skin import Skin


class ButtonValue:
    """A MIDI value with equality/bool semantics (basis of ``Color``)."""

    midi_value: int

    def __init__(self, midi_value: Optional[int] = None, *a: Any, **k: Any) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __ne__(self, other: Any) -> bool:
        ...

    def __bool__(self) -> bool:
        ...


ON_VALUE: ButtonValue
OFF_VALUE: ButtonValue


class Color(ButtonValue):
    """A button color; ``draw`` sends the MIDI bytes that light the button."""

    def draw(self, interface: "ButtonElement") -> None:
        ...


class DummyUndoStepHandler:
    def begin_undo_step(self) -> None:
        ...

    def end_undo_step(self) -> None:
        ...


class ButtonElement(InputControlElement):
    """A momentary/sustain button mapped to a MIDI note or CC."""

    _skin: Optional[Skin]

    def __init__(self, is_momentary: bool, msg_type: int, channel: int,
                 identifier: int, skin: Optional[Skin] = None,
                 undo_step_handler: Optional[DummyUndoStepHandler] = None,
                 *a: Any, **k: Any) -> None:
        ...

    def is_momentary(self) -> bool:
        ...

    def message_map_mode(self) -> int:
        ...

    def is_pressed(self) -> bool:
        ...

    def set_light(self, value: Any) -> None:
        """Light the button with a skin color name, Color, or MIDI value."""
        ...

    def turn_on(self) -> None:
        ...

    def turn_off(self) -> None:
        ...

    def receive_value(self, value: int) -> None:
        ...

    def disconnect(self) -> None:
        ...
