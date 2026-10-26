import traceback

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from .ConfigurableButtonElement import ConfigurableButtonElement
from .MainSelectorComponent import MainSelectorComponent
from .NoteRepeatComponent import NoteRepeatComponent
from .M4LInterface import M4LInterface
from .Log import log
from .Settings import Settings

import typing

# "Type-checking only" guard. Mirrors typing.TYPE_CHECKING (False at runtime)
# via getattr so it also works on Python < 3.8, where the attribute is absent.
_TYPE_CHECKING = getattr(typing, "TYPE_CHECKING", False)

if _TYPE_CHECKING:
    from .contracts import HostApi, ControlSurfaceFacade
    from .surface_core import SurfaceCore

DO_COMBINE = Live.Application.combine_apcs()  # requires 8.2 & higher


LP_MINI_MK3_FAMILY_CODE = (19, 1)
LP_MINI_MK3_ID = 13
LP_X_FAMILY_CODE = (3, 1)
LP_X_ID = 12

#LAYOUT_COMMAND = 0
#FADER_COMMAND = 1
#NOTE_LAYOUT_COMMAND = 15

SYSEX_START = 240
SYSEX_END = 247
SYSEX_GENERAL_INFO = 6
SYSEX_NON_REALTIME = 126
SYSEX_IDENTITY_REQUEST_ID = 1
#SYSEX_IDENTITY_RESPONSE_ID = 2
SYSEX_IDENTITY_REQUEST_MESSAGE = (SYSEX_START,SYSEX_NON_REALTIME,127,SYSEX_GENERAL_INFO,SYSEX_IDENTITY_REQUEST_ID,SYSEX_END)
NOVATION_MANUFACTURER_ID = (0, 32, 41)
FIRMWARE_MODE_COMMAND = 16
#DAW_MODE = 1
STANDALONE_MODE = 0
#SESSION_LAYOUT = 0
#NOTE_LAYOUT = 1
#KEYS_LAYOUT = 5
#FADERS_LAYOUT = 13
#SCALE_LAYOUT = 0
#DRUM_LAYOUT = 1

STD_MSG_HEADER = (SYSEX_START,) + NOVATION_MANUFACTURER_ID + (2, )


def _grid_note_classic(row, column):
	# classic Launchpad grid: row-major, 16 notes per row
	return row * 16 + column


def _grid_note_rgb(row, column):
	# MK2 / MK3 / LPX grid: buttons are assigned "top to bottom"
	return (81 - 10 * row) + column


class LaunchpadBase(ControlSurface):

	# Class-level annotation is evaluated at runtime (no `from __future__
	# import annotations` here); typing is imported above, so this is safe.
	_active_instances: typing.List["LaunchpadBase"] = []

	# Hardware model flags. Class-level so the per-model subclasses
	# (LP_MK1 / LP_MK2 / LP_MK3 / LP_X) can set them declaratively; the
	# auto-detecting ``Launchpad`` sets them as instance attributes when the
	# challenge response identifies the model. Read by SpecialSessionComponent
	# and SpecialProSessionComponent — keep the semantics: MK3 and LPX leave
	# ``_mk2_rgb`` False.
	_lpx = False
	_mk2_rgb = False
	_mk3_rgb = False

	# Skin (button color palette): assigned by the subclass before
	# _build_controls() runs — in __init__ for the per-model classes
	# (LP_MK1 / LP_MK2 / LP_MK3 / LP_X), in init() for the auto-detecting
	# Launchpad once the model is known.
	_skin = None

	@property
	def host_api(self) -> "HostApi":
		"""The Ableton host object (Live.MidiRemoteScript) — the single seam
		between our code and Live. Typed against the HostApi contract."""
		return self._c_instance
	
	def __init__(self, *a, **k):
		ControlSurface.__init__(self, *a, **k)
		live = Live.Application.get_application()
		self._live_major_version = live.get_major_version()
		self._live_minor_version = live.get_minor_version()
		self._live_bugfix_version = live.get_bugfix_version()
		self._selector = None #needed because update hardware is called.
		with self.component_guard():
			self._suppress_send_midi = True
			self._suppress_session_highlight = True
			self._suggested_input_port = ("Launchpad", "Launchpad Mini", "Launchpad S", "Launchpad MK2", "Launchpad X", "Launchpad Mini MK3")
			self._suggested_output_port = ("Launchpad", "Launchpad Mini", "Launchpad S", "Launchpad MK2", "Launchpad X", "Launchpad Mini MK3")				
			self._control_is_with_automap = False
			self._user_byte_write_button = None
			self._config_button = None
			self._wrote_user_byte = False
			self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
			self._init_done = False
			self._surface_core = None
		# construction continues in _build_controls(): eagerly for the
		# per-model classes, once the challenge response identifies the
		# model for the auto-detecting Launchpad.

	def _build_controls(self):
		# second part of the __init__: builds the hardware controls and the
		# main mode component. The hardware-specific configuration
		# (``_side_notes``, ``_drum_notes``, ``_grid_note``,
		# ``_top_button_cc_base``, ``_side_button_midi_type``) is provided by
		# the subclass: as class attributes on the per-model classes
		# (LP_MK1 / LP_MK2 / LP_MK3 / LP_X), as instance attributes on the
		# auto-detecting Launchpad (set by its init()). The skin
		# (``self._skin``) is likewise assigned by the subclass before this
		# method is called.
		self._init_done = True
		assert self._skin is not None, "subclass must assign self._skin before _build_controls()"
		with self.component_guard():
			is_momentary = True
			self._config_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 0, optimized_send_midi=False)
			self._config_button.add_value_listener(self._config_value)
			self._user_byte_write_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 16)
			self._user_byte_write_button.name = 'User_Byte_Button'
			self._user_byte_write_button.send_value(1)
			self._user_byte_write_button.add_value_listener(self._user_byte_value)
			matrix = ButtonMatrixElement()
			matrix.name = 'Button_Matrix'
			for row in range(8):
				button_row = []
				for column in range(8):
					midi_note = self._grid_note(row, column)
					button = ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, midi_note, skin = self._skin, control_surface = self)
					button.name = str(column) + '_Clip_' + str(row) + '_Button'
					button_row.append(button)
				matrix.add_row(tuple(button_row))

			top_buttons = [ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, self._top_button_cc_base + index, skin = self._skin) for index in range(8)]
			side_buttons = [ConfigurableButtonElement(is_momentary, self._side_button_midi_type, 0, self._side_notes[index], skin = self._skin) for index in range(8)]
				
			top_buttons[0].name = 'Bank_Select_Up_Button'
			top_buttons[1].name = 'Bank_Select_Down_Button'
			top_buttons[2].name = 'Bank_Select_Left_Button'
			top_buttons[3].name = 'Bank_Select_Right_Button'
			top_buttons[4].name = 'Session_Button'
			top_buttons[5].name = 'User1_Button'
			top_buttons[6].name = 'User2_Button'
			top_buttons[7].name = 'Mixer_Button'
			side_buttons[0].name = 'Vol_Button'
			side_buttons[1].name = 'Pan_Button'
			side_buttons[2].name = 'SndA_Button'
			side_buttons[3].name = 'SndB_Button'
			side_buttons[4].name = 'Stop_Button'
			side_buttons[5].name = 'Trk_On_Button'
			side_buttons[6].name = 'Solo_Button'
			side_buttons[7].name = 'Arm_Button'
			self._osd = M4LInterface()
			self._osd.name = "OSD"
			self._init_note_repeat()
			try:
				self._selector = MainSelectorComponent(matrix, tuple(top_buttons), tuple(side_buttons), self._config_button, self._osd, self, self._note_repeat, self._c_instance)
			except Exception as e:
				log("Could not create MainSelectorComponent: \n" + str(e))
				log(traceback.format_exc())
				raise e
			self._selector.name = 'Main_Modes'
			self._do_combine()
			for control in self.controls:
				if isinstance(control, ConfigurableButtonElement):
					control.add_value_listener(self._button_value)
		  
			self._suppress_session_highlight = False
			self.set_highlighting_session_component(self._selector.session_component())
			# due to our 2 stage init, we need to rebuild midi map 
			self.request_rebuild_midi_map()
			# and request update 
			self._selector.update()

	def disconnect(self):
		self._suppress_send_midi = True
		for control in self.controls:
			if isinstance(control, ConfigurableButtonElement):
				control.remove_value_listener(self._button_value)
		self._do_uncombine()
		if self._selector is not None:
			self._user_byte_write_button.remove_value_listener(self._user_byte_value)
			self._config_button.remove_value_listener(self._config_value)
		ControlSurface.disconnect(self)
		self._suppress_send_midi = False
		self._send_disconnect_message()
		if self._config_button is not None:
			self._config_button.send_value(32)#Send enable flashing led config message to LP
			self._config_button.send_value(0)
			self._config_button = None
		if self._user_byte_write_button is not None:
			self._user_byte_write_button.send_value(0)
			self._user_byte_write_button = None

	def _combine_active_instances():  # type: ignore[misc]
		# py2-style staticmethod (assigned below); no `self` by design.
		offset = 0
		for instance in LaunchpadBase._active_instances:
			instance._activate_combination_mode(offset)
			offset += instance._selector._session.width()

	_combine_active_instances = staticmethod(_combine_active_instances)

	def _activate_combination_mode(self, track_offset):
		if(Settings.STEPSEQ__LINK_WITH_SESSION):
			self._selector._stepseq.link_with_step_offset(track_offset)
		if(Settings.SESSION__LINK):
			self._selector._session.link_with_track_offset(track_offset)

	def _do_combine(self):
		if (DO_COMBINE and (self not in LaunchpadBase._active_instances)):
			LaunchpadBase._active_instances.append(self)
			LaunchpadBase._combine_active_instances()

	def _do_uncombine(self):
		if self in LaunchpadBase._active_instances:
			LaunchpadBase._active_instances.remove(self)
			if(Settings.SESSION__LINK):
				self._selector._session.unlink()
			if(Settings.STEPSEQ__LINK_WITH_SESSION):
				self._selector._stepseq.unlink()
			LaunchpadBase._combine_active_instances()

	def refresh_state(self):
		ControlSurface.refresh_state(self)
		self.schedule_message(5, self._update_hardware)

	def build_midi_map(self, midi_map_handle):
		ControlSurface.build_midi_map(self, midi_map_handle)
		if self._selector is not None:
			if self._selector._main_mode_index==1:
				mode = Settings.USER_MODES_1[self._selector._sub_mode_list[self._selector._main_mode_index] ]
				if mode != "instrument":
					new_channel = self._selector.channel_for_current_mode()
					for note in self._drum_notes:
						self._translate_message(MIDI_NOTE_TYPE, note, 0, note, new_channel)
			elif self._selector._main_mode_index==2:
				mode = Settings.USER_MODES_2[self._selector._sub_mode_list[self._selector._main_mode_index] ] 
				#self._selector.mode_index == 1:
				#if self._selector._sub_mode_list[self._selector._mode_index] > 0:  # disable midi map rebuild for instrument mode to prevent light feedback errors


	def _send_midi(self, midi_bytes, optimized=None):
		sent_successfully = False
		if not self._suppress_send_midi:
			sent_successfully = ControlSurface._send_midi(self, midi_bytes, optimized=optimized)
		return sent_successfully

	def _update_hardware(self):
		self._suppress_send_midi = False
		if self._user_byte_write_button is not None:
			self._user_byte_write_button.send_value(1)
			self._wrote_user_byte = True
		self._suppress_send_midi = True
		self.set_enabled(False)
		self._suppress_send_midi = False
		self._send_challenge()

	def _send_disconnect_message(self):
		# hook for the hardware-specific quit SYSEX sent on disconnect;
		# the classic (mk1) pad needs none, so the base sends nothing.
		pass

	def _user_byte_value(self, value):
		assert (value in range(128))
		if not self._wrote_user_byte:
			enabled = (value == 1)
			self._control_is_with_automap = not enabled
			self._suppress_send_midi = self._control_is_with_automap
			if not self._control_is_with_automap:
				for control in self.controls:
					if isinstance(control, ConfigurableButtonElement):
						control.force_next_send()

			self._selector.set_mode(0)
			self.set_enabled(enabled)
			self._suppress_send_midi = False
		else:
			self._wrote_user_byte = False

	def _button_value(self, value):
		assert value in range(128)

	def _config_value(self, value):
		assert value in range(128)

	def _set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
		if not self._suppress_session_highlight:
			ControlSurface._set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks)
			
	def _init_note_repeat(self):
		self._note_repeat = NoteRepeatComponent(name='Note_Repeat')
		self._note_repeat.set_enabled(False)
		self._note_repeat.set_note_repeat(self._c_instance.note_repeat)

	# Phase 4b: SurfaceCore integration - delegate to facade while maintaining compatibility
	def _get_surface_core(self) -> typing.Optional["SurfaceCore"]:
		"""Get or create the SurfaceCore facade for this control surface."""
		if getattr(self, '_surface_core', None) is None:
			try:
				from .surface_core import SurfaceCore
				self._surface_core = SurfaceCore(self, getattr(self, '_c_instance', None))
			except Exception:
				self._surface_core = None
		return self._surface_core

	@property
	def core(self) -> typing.Union["SurfaceCore", "LaunchpadBase"]:
		"""Access to the SurfaceCore facade."""
		core = self._get_surface_core()
		if core is not None:
			return core
		# Fallback to self if core not available
		return self

