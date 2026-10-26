"""Launchpad 95 for the Launchpad MK2.

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MK2
challenge is sent (sysex 240,0,32,41,2,24,64 + 4 bytes) and the validated
response enables MIDI out.
"""

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_NOTE_TYPE

from .LaunchpadBase import LaunchpadBase, _grid_note_rgb

# The @Reimport marker is Live-specific: on script reimport, only
# __init__.py is re-executed and other modules stay cached. With this
# marker Live re-runs the import, so edits to SkinMK2.py take effect
# without restarting Live. It is a no-op outside Live (e.g. pytest).
from .SkinMK2 import make_skin  # @Reimport


class LP_MK2(LaunchpadBase):
	"""Launchpad MK2: RGB, mk2 grid layout (81-10*row+col)."""

	_mk2_rgb = True

	# hardware-specific configuration, consumed by LaunchpadBase._build_controls()
	_side_notes = (89, 79, 69, 59, 49, 39, 29, 19)
	_drum_notes = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)
	_grid_note = staticmethod(_grid_note_rgb)
	_top_button_cc_base = 104
	_side_button_midi_type = MIDI_NOTE_TYPE

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self._skin = make_skin()
		self._build_controls()
		self.log_message("LaunchPad95 (mk2) Loaded !")

	def _send_challenge(self):
		# mk2 challenge: sysex with 4 challenge bytes
		challenge_bytes = tuple([ self._challenge >> 8 * index & 127 for index in range(4) ])
		self._send_midi((240, 0, 32, 41, 2, 24, 64) + challenge_bytes + (247,))

	def _send_disconnect_message(self):
		# launchpad mk2 needs disconnect string sent
		self._send_midi((240, 0, 32, 41, 2, 24, 64, 247))

	def handle_sysex(self, midi_bytes):
		if len(midi_bytes) == 10 and midi_bytes[:7] == (240, 0, 32, 41, 2, 24, 64):
			response = int(midi_bytes[7])
			response += int(midi_bytes[8]) << 8
			if response == Live.Application.encrypt_challenge2(self._challenge):
				self.log_message("Challenge Response ok (mk2)")
				self._suppress_send_midi = False
				self.set_enabled(True)
		else:
			ControlSurface.handle_sysex(self, midi_bytes)
