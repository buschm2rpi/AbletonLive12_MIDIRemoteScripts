from __future__ import annotations
from typing import Any, Dict, Optional

from _Framework.Skin import SkinColorMissingError
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE


class ConfigurableButtonElement(ButtonElement):
    """
    Special button class (adapted from Push script for LP Pro)
    that can be configured with custom on- and off-values.

    A ConfigurableButtonElement can have states other than True or
    False, which can be defined by setting the 'states' property.
    Thus 'set_light' can take any state or skin color.
    """

    default_states: Dict[bool, str] = {
        True: "DefaultButton.On",
        False: "DefaultButton.Off",
    }
    send_depends_on_forwarding: bool = False

    def __init__(
        self,
        is_momentary: bool,
        msg_type: int,
        channel: int,
        identifier: int,
        skin: Any = None,
        default_states: Optional[Dict[bool, str]] = None,
        control_surface: Any = None,
        *a: Any,
        **k: Any,
    ) -> None:
        self._control_surface = control_surface
        super(ConfigurableButtonElement, self).__init__(
            is_momentary, msg_type, channel, identifier, skin=skin, **k
        )
        if default_states is not None:
            self.default_states = default_states
        self.states: Dict[bool, str] = dict(self.default_states)

    @property
    def _on_value(self) -> str:
        return self.states[True]

    @property
    def _off_value(self) -> str:
        return self.states[False]

    @property
    def on_value(self) -> Any:
        return self._try_fetch_skin_value(self._on_value)

    @property
    def off_value(self) -> Any:
        return self._try_fetch_skin_value(self._off_value)

    def _try_fetch_skin_value(self, value: str) -> Any:
        try:
            return self._skin[value]
        except SkinColorMissingError:
            return value

    def reset(self) -> None:
        self.set_light("DefaultButton.Disabled")
        # self.reset_state()

    def reset_state(self) -> None:
        self.states = dict(self.default_states)
        super(ConfigurableButtonElement, self).reset_state()
        self.set_enabled(True)

    def set_on_off_values(self, on_value: Any, off_value: Optional[Any] = None) -> None:
        self.clear_send_cache()
        if off_value is None:
            self.states[True] = str(on_value) + ".On"
            self.states[False] = str(on_value) + ".Off"
        else:
            self.states[True] = on_value
            self.states[False] = off_value

    def set_enabled(self, enabled: bool) -> None:
        self.suppress_script_forwarding = not enabled

    def is_enabled(self) -> bool:
        return not self.suppress_script_forwarding

    def set_light(self, value: Any) -> None:
        try:
            self._draw_skin(value)
        except SkinColorMissingError:
            super(ButtonElement, self).set_light(value)

    def send_value(self, value: Any, force: Any = None, channel: Any = None) -> Any:
        if value is ON_VALUE:
            self._do_send_on_value(channel=channel)
        elif value is OFF_VALUE:
            self._do_send_off_value(channel=channel)
        elif type(value) is int:
            super(ConfigurableButtonElement, self).send_value(
                value, force=force, channel=channel
            )
        else:
            self._draw_skin(value)

    def force_next_send(self) -> None:
        """
        Enforces sending the next value regardless of wether the
        control is mapped to the script.
        """
        self._force_next_send = True
        self.clear_send_cache()

    def _do_send_on_value(self, channel: Any = None) -> None:
        if type(self._on_value) is int:
            super(ConfigurableButtonElement, self).send_value(
                self._on_value, channel=channel
            )
        else:
            self._draw_skin(self._on_value)

    def _do_send_off_value(self, channel: Any = None) -> None:
        if type(self._off_value) is int:
            super(ConfigurableButtonElement, self).send_value(
                self._off_value, channel=channel
            )
        else:
            self._draw_skin(self._off_value)

    def _draw_skin(self, value: Any) -> None:
        self._skin[value].draw(self)

    def script_wants_forwarding(self) -> bool:
        return not self.suppress_script_forwarding
