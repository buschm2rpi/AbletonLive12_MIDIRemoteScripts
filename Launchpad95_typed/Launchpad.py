"""Auto-detecting Launchpad entry point (kept for backward compatibility).

Detects the connected model at runtime from the challenge response
(``handle_sysex``) and defers full construction to ``init()``. The model
flags set by the handshake are mapped onto the hardware-specific
configuration attributes consumed by ``LaunchpadBase._build_controls()``.

For statically configured models see ``LP_MK1`` / ``LP_MK2`` / ``LP_MK3``
/ ``LP_X`` instead.
"""

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE

from .LaunchpadBase import (
	LaunchpadBase,
	STD_MSG_HEADER,
	LP_MINI_MK3_ID,
	LP_X_ID,
	SYSEX_END,
	SYSEX_IDENTITY_REQUEST_MESSAGE,
	FIRMWARE_MODE_COMMAND,
	STANDALONE_MODE,
	_grid_note_classic,
	_grid_note_rgb,
)

# The @Reimport marker is Live-specific: on script reimport, only
# __init__.py is re-executed and other modules stay cached. With this
# marker Live re-runs these imports, so edits to SkinMK1.py / SkinMK2.py
# take effect without restarting Live. It is a no-op outside Live (e.g. pytest).
from .SkinMK1 import make_skin as make_skin_mk1  # @Reimport
from .SkinMK2 import make_skin as make_skin_mk2  # @Reimport


class Launchpad(LaunchpadBase):
	"""Auto-detecting entry point (kept for backward compatibility).

	Detects the connected model at runtime from the challenge response
	(see ``handle_sysex``) and defers full construction to
	``init()``. For statically configured models see ``LP_MK1`` / ``LP_MK2``
	/ ``LP_MK3`` / ``LP_X`` instead.
	"""

	def init(self) -> None:
		#skip init if already done.
		if self._init_done:
			return

		# map the model identified by the challenge response onto the
		# hardware-specific configuration consumed by _build_controls()
		if self._mk3_rgb or self._lpx:
			self._skin = make_skin_mk2()
			self._side_notes = (89, 79, 69, 59, 49, 39, 29, 19)
			self._drum_notes = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
			self._grid_note = _grid_note_rgb
			self._top_button_cc_base = 91
			self._side_button_midi_type = MIDI_CC_TYPE
		elif self._mk2_rgb:
			self._skin = make_skin_mk2()
			self._side_notes = (89, 79, 69, 59, 49, 39, 29, 19)
			self._drum_notes = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
			self._grid_note = _grid_note_rgb
			self._top_button_cc_base = 104
			self._side_button_midi_type = MIDI_NOTE_TYPE
		else:
			self._skin = make_skin_mk1()
			self._side_notes = (8, 24, 40, 56, 72, 88, 104, 120)
			self._drum_notes = (41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 89, 90, 91, 92, 93, 94, 95, 105, 106, 107)
			self._grid_note = _grid_note_classic
			self._top_button_cc_base = 104
			self._side_button_midi_type = MIDI_NOTE_TYPE

		self._build_controls()
		# the model is only known at runtime, so the loaded banner is
		# dispatched on the flags set by handle_sysex()
		if self._lpx:
			self.log_message("LaunchPad95 (LPX) Loaded !")
		elif self._mk3_rgb:
			self.log_message("LaunchPad95 (mk3) Loaded !")
		elif self._mk2_rgb:
			self.log_message("LaunchPad95 (mk2) Loaded !")
		else:
			self.log_message("LaunchPad95 (classic) Loaded !")

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

	def _send_disconnect_message(self) -> None:
		# the model is only known at runtime (from the challenge response),
		# so dispatch on the model flags set by handle_sysex()
		if self._lpx:
			# lpx needs disconnect string sent
			self._send_midi(STD_MSG_HEADER + (LP_X_ID, 14, 0, SYSEX_END))
			self._send_midi(STD_MSG_HEADER + (LP_X_ID, FIRMWARE_MODE_COMMAND, STANDALONE_MODE, SYSEX_END))
		elif self._mk3_rgb:
			# launchpad mini mk3 needs disconnect string sent
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 14, 0, SYSEX_END))
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, FIRMWARE_MODE_COMMAND, STANDALONE_MODE, SYSEX_END))
		elif self._mk2_rgb:
			# launchpad mk2 needs disconnect string sent
			self._send_midi((240, 0, 32, 41, 2, 24, 64, 247))

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
