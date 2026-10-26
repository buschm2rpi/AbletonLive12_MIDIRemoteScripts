"""Launchpad 95 for the Launchpad Mini MK3.

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MIDI
identity request is sent, and on the Mini MK3 identity response the script
switches the pad to programmer mode and enables MIDI out.
"""

from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE

from .LaunchpadBase import (
	LaunchpadBase,
	LP_MINI_MK3_FAMILY_CODE,
	LP_MINI_MK3_ID,
	SYSEX_END,
	SYSEX_IDENTITY_REQUEST_MESSAGE,
	STD_MSG_HEADER,
	FIRMWARE_MODE_COMMAND,
	STANDALONE_MODE,
	_grid_note_rgb,
)

# The @Reimport marker is Live-specific: on script reimport, only
# __init__.py is re-executed and other modules stay cached. With this
# marker Live re-runs the import, so edits to SkinMK2.py take effect
# without restarting Live. It is a no-op outside Live (e.g. pytest).
from .SkinMK2 import make_skin  # @Reimport


class LP_MK3(LaunchpadBase):
	"""Launchpad Mini MK3: RGB, mk2 grid layout, CC top/side buttons."""

	_mk3_rgb = True

	# hardware-specific configuration, consumed by LaunchpadBase._build_controls()
	_side_notes = (89, 79, 69, 59, 49, 39, 29, 19)
	_drum_notes = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
	_grid_note = staticmethod(_grid_note_rgb)
	_top_button_cc_base = 91
	_side_button_midi_type = MIDI_CC_TYPE

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self._skin = make_skin()
		self._build_controls()
		self.log_message("LaunchPad95 (mk3) Loaded !")

	def _send_challenge(self):
		# mk3 has no challenge: ask for the MIDI identity instead
		self._send_midi(SYSEX_IDENTITY_REQUEST_MESSAGE)

	def _send_disconnect_message(self):
		# launchpad mini mk3 needs disconnect string sent
		self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 14, 0, SYSEX_END))
		self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, FIRMWARE_MODE_COMMAND, STANDALONE_MODE, SYSEX_END))

	def handle_sysex(self, midi_bytes):
		if len(midi_bytes) >= 12 and midi_bytes[:8] == (240, 126, 0, 6, 2, 0, 32, 41) and midi_bytes[8:10] == LP_MINI_MK3_FAMILY_CODE:
			#programmer mode
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 14, 1, SYSEX_END))
			#led feedback: internal off, external on
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 10, 0, 1, SYSEX_END))
			#disable sleep mode
			self._send_midi(STD_MSG_HEADER + (LP_MINI_MK3_ID, 9, 1, SYSEX_END))
			self._suppress_send_midi = False
			self.set_enabled(True)
		else:
			ControlSurface.handle_sysex(self, midi_bytes)
