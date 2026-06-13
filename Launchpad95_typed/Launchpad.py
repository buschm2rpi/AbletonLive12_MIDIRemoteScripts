from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, Optional, Tuple

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

if TYPE_CHECKING:
    from typing import Any as FrameworkType

    # _Framework types are only available at runtime inside Ableton Live.
    # These imports are used for static type checking only.
    from _Framework.ControlSurface import ControlSurface as _ControlSurfaceType
    from _Framework.ButtonElement import ButtonElement as _ButtonElementType
    from _Framework.ButtonMatrixElement import ButtonMatrixElement as _ButtonMatrixElementType
    from .ConfigurableButtonElement import ConfigurableButtonElement as _ConfigurableButtonElementType
    from .MainSelectorComponent import MainSelectorComponent as _MainSelectorComponentType
    from .NoteRepeatComponent import NoteRepeatComponent as _NoteRepeatComponentType
    from .M4LInterface import M4LInterface as _M4LInterfaceType

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


class Launchpad(ControlSurface):

	_active_instances: list[Launchpad] = []

	def __init__(self, c_instance: Any) -> None:
		ControlSurface.__init__(self, c_instance)
		live = Live.Application.get_application()
		self._live_major_version: int = live.get_major_version()
		self._live_minor_version: int = live.get_minor_version()
		self._live_bugfix_version: int = live.get_bugfix_version()
		self._selector: Optional[MainSelectorComponent] = None  # needed because update hardware is called
		self._lpx: bool = False
		self._mk2_rgb: bool = False
		self._mk3_rgb: bool = False
		with self.component_guard():
			self._suppress_send_midi: bool = True
			self._suppress_session_highlight: bool = True
			self._suggested_input_port: Tuple[str, ...] = ("Launchpad", "Launchpad Mini", "Launchpad S", "Launchpad MK2", "Launchpad X", "Launchpad Mini MK3")
			self._suggested_output_port: Tuple[str, ...] = ("Launchpad", "Launchpad Mini", "Launchpad S", "Launchpad MK2", "Launchpad X", "Launchpad Mini MK3")
			self._control_is_with_automap: bool = False
			self._user_byte_write_button: Optional[ButtonElement] = None
			self._config_button: Optional[ButtonElement] = None
			self._wrote_user_byte: bool = False
			self._challenge: int = Live.Application.get_random_int(0, 400000000) & 2139062143
			self._init_done: bool = False
		# caller will send challenge and we will continue as challenge is received.
		# These are set during init() after hardware detection.
		self._skin: object  # type: ignore[assignment]
		self._osd: M4LInterface  # type: ignore[assignment]
		self._note_repeat: NoteRepeatComponent  # type: ignore[assignment]
		
			
	def init(self) -> None:
		#skip init if already done.
		if self._init_done:
			return
		self._init_done = True
		
		# second part of the __init__ after model has been identified using its challenge response
		if self._mk3_rgb or self._lpx:
			from .SkinMK2 import make_skin
			self._skin = make_skin()
			self._side_notes: Tuple[int, ...] = (89, 79, 69, 59, 49, 39, 29, 19)
			self._drum_notes: Tuple[int, ...] = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
		elif self._mk2_rgb:
			from .SkinMK2 import make_skin
			self._skin = make_skin()
			self._side_notes: Tuple[int, ...] = (89, 79, 69, 59, 49, 39, 29, 19)
			#self._drum_notes = (20, 30, 31, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
			self._drum_notes: Tuple[int, ...] = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
		else:
			from .SkinMK1 import make_skin  # @Reimport
			self._skin = make_skin()
			self._side_notes: Tuple[int, ...] = (8, 24, 40, 56, 72, 88, 104, 120)
			self._drum_notes: Tuple[int, ...] = (41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 89, 90, 91, 92, 93, 94, 95, 105, 106, 107)
		
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
					if self._mk2_rgb or self._mk3_rgb or self._lpx:
						# for mk2 buttons are assigned "top to bottom"
						midi_note = (81 - (10 * row)) + column
					else:
						midi_note = row * 16 + column
					button = ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, midi_note, skin = self._skin, control_surface = self)
					button.name = str(column) + '_Clip_' + str(row) + '_Button'
					button_row.append(button)
				matrix.add_row(tuple(button_row))

			if self._mk3_rgb or self._lpx :
				top_buttons = [ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, 91 + index, skin = self._skin) for index in range(8)]
				side_buttons = [ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, self._side_notes[index], skin = self._skin) for index in range(8)]
			else:
				top_buttons = [ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, 104 + index, skin = self._skin) for index in range(8)]
				side_buttons = [ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, self._side_notes[index], skin = self._skin) for index in range(8)]
				
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
			if self._lpx:
				self.log_message("LaunchPad95 (LPX) Loaded !")
			elif self._mk3_rgb:
				self.log_message("LaunchPad95 (mk3) Loaded !")
			elif self._mk2_rgb:
				self.log_message("LaunchPad95 (mk2) Loaded !")
			else:
				self.log_message("LaunchPad95 (classic) Loaded !")
				
	def disconnect(self) -> None:
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
		if self._lpx:
			# lpx needs disconnect string sent
			self._send_midi(STD_MSG_HEADER + (LP_X_ID, 14, 0, SYSEX_END))
			self._send_midi(STD_MSG_HEADER + (LP_X_ID, FIRMWARE_MODE_COMMAND, STANDALONE_MODE, SYSEX_END))
		elif self._mk3_rgb:
			# launchpad mk2 needs disconnect string sent
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 14, 0, SYSEX_END))
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, FIRMWARE_MODE_COMMAND, STANDALONE_MODE, SYSEX_END))
		elif self._mk2_rgb:
			# launchpad mk2 needs disconnect string sent
			self._send_midi((240, 0, 32, 41, 2, 24, 64, 247))
		if self._config_button is not None:
			self._config_button.send_value(32)#Send enable flashing led config message to LP
			self._config_button.send_value(0)
			self._config_button = None
		if self._user_byte_write_button is not None:
			self._user_byte_write_button.send_value(0)
			self._user_byte_write_button = None

	def _combine_active_instances() -> None:  # type: ignore[misc]
		support_devices = False
		for instance in Launchpad._active_instances:
			support_devices |= (instance._device_component is not None)  # type: ignore[attr-defined]
		offset = 0
		for instance in Launchpad._active_instances:
			instance._activate_combination_mode(offset, support_devices)
			offset += instance._selector._session.width()  # type: ignore[union-attr]

	_combine_active_instances = staticmethod(_combine_active_instances)

	def _activate_combination_mode(self, track_offset: int, support_devices: bool) -> None:
		if(Settings.STEPSEQ__LINK_WITH_SESSION):
			self._selector._stepseq.link_with_step_offset(track_offset)
		if(Settings.SESSION__LINK):
			self._selector._session.link_with_track_offset(track_offset)

	def _do_combine(self) -> None:
		if (DO_COMBINE and (self not in Launchpad._active_instances)):
			Launchpad._active_instances.append(self)
			Launchpad._combine_active_instances()

	def _do_uncombine(self) -> None:
		if self in Launchpad._active_instances:
			Launchpad._active_instances.remove(self)
			if(Settings.SESSION__LINK):
				self._selector._session.unlink()
			if(Settings.STEPSEQ__LINK_WITH_SESSION):
				self._selector._stepseq.unlink()
			Launchpad._combine_active_instances()

	def refresh_state(self) -> None:
		ControlSurface.refresh_state(self)
		self.schedule_message(5, self._update_hardware)

	def handle_sysex(self, midi_bytes: tuple[int, ...]) -> None:
		if len(midi_bytes) >= 10 and midi_bytes[:8] == (240, 126, 0, 6, 2, 0, 32, 41): #0,32,41=novation
			if len(midi_bytes) >= 12 and midi_bytes[8:10] == (19,1):
				self._mk3_rgb = True
				#programmer mode
				self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 14, 1, SYSEX_END))
				#led feedback: internal off, external on
				self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 10, 0, 1, SYSEX_END))
				#disable sleep mode
				self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 9, 1, SYSEX_END))
				self._suppress_send_midi = False
				self.set_enabled(True)
				self.init()
			elif len(midi_bytes) >= 12 and midi_bytes[8:10] == (3,1):
				self._lpx = True
				#programmer mode
				self._send_midi(STD_MSG_HEADER + (LP_X_ID, 14, 1, SYSEX_END))
				#led feedback: internal off, external on
				self._send_midi(STD_MSG_HEADER + (LP_X_ID, 10, 0, 1, SYSEX_END))
				#disable sleep mode
				self._send_midi(STD_MSG_HEADER + (LP_X_ID, 9, 1, SYSEX_END))
				self._suppress_send_midi = False
				self.set_enabled(True)
				self.init()
			else:
				ControlSurface.handle_sysex(self,midi_bytes)
				#self.log_message("OTHER NOVATION")

		# MK2 has different challenge and params
		elif len(midi_bytes) == 10 and midi_bytes[:7] == (240, 0, 32, 41, 2, 24, 64):
			response = int(midi_bytes[7])
			response += int(midi_bytes[8]) << 8
			if response == Live.Application.encrypt_challenge2(self._challenge):
				self.log_message("Challenge Response ok (mk2)")
				self._mk2_rgb = True
				self._suppress_send_midi = False
				self.set_enabled(True)
				self.init()
		#MK1 Challenge
		elif len(midi_bytes) == 8 and midi_bytes[1:5] == (0, 32, 41, 6):
			response = int(midi_bytes[5])
			response += int(midi_bytes[6]) << 8
			if response == Live.Application.encrypt_challenge2(self._challenge):
				self.log_message("Challenge Response ok (mk1)")
				self._mk2_rgb = False
				self.init()
				self._suppress_send_midi = False
				self.set_enabled(True)
		else:
			ControlSurface.handle_sysex(self,midi_bytes)
		

	def build_midi_map(self, midi_map_handle: object) -> None:
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


	def _send_midi(self, midi_bytes: tuple[int, ...], optimized: object = None) -> bool:
		sent_successfully = False
		if not self._suppress_send_midi:
			sent_successfully = ControlSurface._send_midi(self, midi_bytes, optimized=optimized)
		return sent_successfully

	def _update_hardware(self) -> None:
		self._suppress_send_midi = False
		if self._user_byte_write_button is not None:
			self._user_byte_write_button.send_value(1)
			self._wrote_user_byte = True
		self._suppress_send_midi = True
		self.set_enabled(False)
		self._suppress_send_midi = False
		self._send_challenge()

	def _send_challenge(self) -> None:
		# send challenge for all models to allow to detect which one is actually plugged
		# mk3 and LPX
		self._send_midi(SYSEX_IDENTITY_REQUEST_MESSAGE)
		# mk2
		challenge_bytes = tuple([ self._challenge >> 8 * index & 127 for index in range(4) ])
		self._send_midi((240, 0, 32, 41, 2, 24, 64) + challenge_bytes + (247,))
		# mk1's
		for index in range(4):
			challenge_byte = self._challenge >> 8 * index & 127
			self._send_midi((176, 17 + index, challenge_byte))

	def _user_byte_value(self, value: int) -> None:
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

	def _button_value(self, value: int) -> None:
		assert value in range(128)

	def _config_value(self, value: int) -> None:
		assert value in range(128)

	def _set_session_highlight(self, track_offset: int, scene_offset: int, width: int, height: int, include_return_tracks: bool) -> None:
		if not self._suppress_session_highlight:
			ControlSurface._set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks)
			
	def _init_note_repeat(self) -> None:
		self._note_repeat = NoteRepeatComponent(name='Note_Repeat')
		self._note_repeat.set_enabled(False)
		self._note_repeat.set_note_repeat(self._c_instance.note_repeat)
