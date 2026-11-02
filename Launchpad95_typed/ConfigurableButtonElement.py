from __future__ import annotations

from _Framework.Skin import SkinColorMissingError
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from _Framework.ButtonElement import ButtonValue
	from _Framework.Skin import Skin
	from .contracts import ControlSurfaceFacade

# A button state value: a skin color name (str) or a raw MIDI value (int).
StateValue = str | int

class ConfigurableButtonElement(ButtonElement):
	"""
	Special button class (adapted from Push script for LP Pro)
	that can be configured with custom on- and off-values.
	
	A ConfigurableButtonElement can have states other than True or
	False, which can be defined by setting the 'states' property.
	Thus 'set_light' can take any state or skin color.
	"""
	default_states: dict[bool, StateValue] = {True: 'DefaultButton.On', False: 'DefaultButton.Off'}
	send_depends_on_forwarding: bool = False
	states: dict[bool, StateValue]
	# LaunchpadBase._build_controls() creates these buttons only after
	# asserting the surface skin is set, so every instance carries a real
	# Skin (narrower than ButtonElement's Optional[Skin]).
	_skin: Skin
	# Set by InputControlElement.__init__; redeclared here because the
	# stubbed base class does not declare it.
	_force_next_send: bool

	def __init__(self, is_momentary: bool, msg_type: int, channel: int,
	             identifier: int, skin: Skin | None = None,
	             default_states: dict[bool, StateValue] | None = None,
	             control_surface: ControlSurfaceFacade | None = None,
	             *a: Any, **k: Any) -> None:
		self._control_surface: ControlSurfaceFacade | None = control_surface
		super(ConfigurableButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, skin = skin, **k)
		if default_states is not None:
			self.default_states = default_states
		self.states = dict(self.default_states)

	@property
	def _on_value(self) -> StateValue:
		return self.states[True]

	@property
	def _off_value(self) -> StateValue:
		return self.states[False]

	@property
	def on_value(self) -> Any:
		return self._try_fetch_skin_value(self._on_value)

	@property
	def off_value(self) -> Any:
		return self._try_fetch_skin_value(self._off_value)

	def _try_fetch_skin_value(self, value: StateValue) -> Any:
		try:
			# int values are raw MIDI values and can never be skin keys;
			# the lookup raises SkinColorMissingError and we fall back.
			return self._skin[value]
		except SkinColorMissingError:
			return value

	def reset(self) -> None:
		self.set_light('DefaultButton.Disabled')
		#self.reset_state()

	def reset_state(self) -> None:
		self.states = dict(self.default_states)
		super(ConfigurableButtonElement, self).reset_state()
		self.set_enabled(True)

	def set_on_off_values(self, on_value: StateValue, off_value: StateValue | None = None) -> None:
		self.clear_send_cache()
		if off_value is None:
			self.states[True] = str(on_value)+".On"
			self.states[False] = str(on_value)+".Off"
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
			# Falls through to ButtonElementMixin.set_light (boolean on/off
			# path), skipping ButtonElement's skin-based set_light.
			super(ButtonElement, self).set_light(value)

	def send_value(self, value: ButtonValue | StateValue, force: bool = False,
	                     channel: int | None = None, **k: Any) -> None:
		if value is ON_VALUE:
			self._do_send_on_value(force=force, channel=channel, **k)
		elif value is OFF_VALUE:
			self._do_send_off_value(force=force, channel=channel, **k)
		elif type(value) is int:
			super(ConfigurableButtonElement, self).send_value(value, force=force, channel=channel, **k)
		else:
			self._draw_skin(value)
			
	def force_next_send(self) -> None:
		"""
		Enforces sending the next value regardless of wether the
		control is mapped to the script.
		"""
		self._force_next_send = True
		self.clear_send_cache()
		
		
	def _do_send_on_value(self, **k: Any) -> None:
		if type(self._on_value) is int:
			super(ConfigurableButtonElement, self).send_value(self._on_value, **k)
		else:
			self._draw_skin(self._on_value)
			
	def _do_send_off_value(self, **k: Any) -> None:
		if type(self._off_value) is int:
			super(ConfigurableButtonElement, self).send_value(self._off_value, **k)
		else:
			self._draw_skin(self._off_value)

	def _draw_skin(self, value: Any) -> None:
		self._skin[value].draw(self)
		
	def script_wants_forwarding(self) -> bool:
		return not self.suppress_script_forwarding
