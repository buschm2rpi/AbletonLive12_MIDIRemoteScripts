"""Type stub for ``_Framework.InputControlElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple

from _Framework.NotifyingControlElement import NotifyingControlElement

# MIDI message type constants (values match real Live).
MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_SYSEX_TYPE = 3
MIDI_INVALID_TYPE = 4

MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224


class InputControlElement(NotifyingControlElement):
    """A control element that maps to a MIDI message (note/CC/pitchbend/sysex)."""

    def __init__(self, msg_type: Optional[int] = None, channel: Optional[int] = None,
                 identifier: Optional[int] = None,
                 sysex_identifier: Optional[Tuple[int, ...]] = None,
                 request_rebuild_midi_map: Any = None,
                 *a: Any, **k: Any) -> None:
        ...

    def message_type(self) -> int:
        ...

    def message_channel(self) -> int:
        ...

    def original_channel(self) -> int:
        ...

    def message_identifier(self) -> int:
        ...

    def original_identifier(self) -> int:
        ...

    def message_sysex_identifier(self) -> Optional[Tuple[int, ...]]:
        ...

    def message_map_mode(self) -> int:
        ...

    @property
    def mapping_sensitivity(self) -> float:
        ...

    @mapping_sensitivity.setter
    def mapping_sensitivity(self, sensitivity: float) -> None:
        ...

    @property
    def suppress_script_forwarding(self) -> bool:
        ...

    @suppress_script_forwarding.setter
    def suppress_script_forwarding(self, value: bool) -> None:
        ...

    def force_next_send(self) -> None:
        ...

    def set_channel(self, channel: int) -> None:
        ...

    def set_identifier(self, identifier: int) -> None:
        ...

    def set_needs_takeover(self, needs_takeover: bool) -> None:
        ...

    def set_feedback_delay(self, delay: int) -> None:
        ...

    def needs_takeover(self) -> bool:
        ...

    def use_default_message(self) -> None:
        ...

    def install_connections(self, install_translation: Callable[..., Any],
                            install_mapping: Callable[..., Any],
                            install_forwarding: Callable[..., Any]) -> None:
        ...

    def script_wants_forwarding(self) -> bool:
        ...

    def begin_gesture(self) -> None:
        ...

    def end_gesture(self) -> None:
        ...

    def connect_to(self, parameter: Any) -> None:
        """Map this control to a Live device parameter."""
        ...

    def release_parameter(self) -> None:
        ...

    def mapped_parameter(self) -> Any:
        ...

    def identifier_bytes(self) -> List[Tuple[int, ...]]:
        ...

    def send_value(self, value: int, force: bool = False,
                   channel: Optional[int] = None) -> None:
        ...

    def clear_send_cache(self) -> None:
        ...

    def reset(self) -> None:
        ...

    def reset_state(self) -> None:
        ...

    def receive_value(self, value: int) -> None:
        ...

    def set_report_values(self, report_input: bool, report_output: bool) -> None:
        ...
