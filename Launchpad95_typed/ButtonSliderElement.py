from __future__ import annotations
from typing import Any, Optional, Tuple

from _Framework.InputControlElement import MIDI_INVALID_TYPE, InputControlElement
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import SlotManager


class ButtonSliderElement(SliderElement, SlotManager):
    _last_sent_value: int
    _buttons: Optional[Tuple[Any, ...]]

    def __init__(self, buttons: Tuple[Any, ...]) -> None:
        SliderElement.__init__(self, MIDI_INVALID_TYPE, 0, 0)
        self._parameter_value_slot = self.register_slot(
            None, self._on_parameter_changed, "value"
        )
        self._buttons = buttons
        self._last_sent_value = -1
        self._button_slots = self.register_slot_manager()
        for button in self._buttons:
            self._button_slots.register_slot(
                button,
                (self._button_value),
                "value",
                extra_kws={"identify_sender": True},
            )

    def disconnect(self) -> None:
        SliderElement.disconnect(self)
        self._buttons = None

    def message_channel(self) -> Any:
        raise NotImplementedError(
            "message_channel() should not be called directly on ButtonSliderElement"
        )

    def message_identifier(self) -> Any:
        raise NotImplementedError(
            "message_identifier() should not be called directly on ButtonSliderElement"
        )

    def message_map_mode(self) -> Any:
        raise NotImplementedError(
            "message_map_mode() should not be called directly on ButtonSliderElement"
        )

    def install_connections(
        self,
        install_translation_callback: Any,
        install_mapping_callback: Any,
        install_forwarding_callback: Any,
    ) -> None:
        pass

    def connect_to(self, parameter: Any) -> None:
        InputControlElement.connect_to(self, parameter)
        self._parameter_value_slot.subject = parameter
        if self._parameter_to_map_to is not None:
            self._on_parameter_changed(trigger_osd=False)

    def release_parameter(self) -> None:
        self._parameter_value_slot.subject = None
        InputControlElement.release_parameter(self)

    def identifier_bytes(self) -> Any:
        raise RuntimeWarning(
            "identifier_bytes() should not be called on ButtonSliderElement"
        )

    def send_value(self, value: Any, force: Any = None, channel: Any = None) -> Any:
        if self._buttons is None:
            return
        if value != self._last_sent_value:
            num_buttons = len(self._buttons)
            index_to_light = 0
            index_to_light = int((num_buttons - 1) * value / 127) if value > 0 else 0
            for index in range(num_buttons):
                if index == index_to_light:
                    self._buttons[index].turn_on()
                else:
                    self._buttons[index].turn_off()

            self._last_sent_value = value

    def _button_value(self, value: int, sender: Any) -> None:
        if self._buttons is None:
            return
        self.clear_send_cache()
        if not (value != 0 or sender.is_momentary()):
            index_of_sender = list(self._buttons).index(sender)
            midi_value = int(127 * index_of_sender / (len(self._buttons) - 1))
            if self._parameter_to_map_to is not None:
                if self._parameter_to_map_to.is_enabled:
                    param_range = (
                        self._parameter_to_map_to.max - self._parameter_to_map_to.min
                    )
                    param_value = (
                        param_range * index_of_sender / (len(self._buttons) - 1)
                        + self._parameter_to_map_to.min
                    )
                    if index_of_sender > 0:
                        param_value += param_range / (4 * len(self._buttons))
                        if param_value > self._parameter_to_map_to.max:
                            param_value = self._parameter_to_map_to.max
                    self._parameter_to_map_to.value = param_value
            self.notify_value(midi_value)

    def _on_parameter_changed(self, trigger_osd: bool = True) -> None:
        param_range = abs(self._parameter_to_map_to.max - self._parameter_to_map_to.min)
        midi_value = int(
            127
            * abs(self._parameter_to_map_to.value - self._parameter_to_map_to.min)
            / param_range
        )
        self.send_value(midi_value)
