"""Launchpad 95 for the classic Launchpad (MK1: Launchpad / S / Mini).

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MK1
challenge is sent (4 CC bytes) and the validated response enables MIDI out.
"""

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_NOTE_TYPE

from .LaunchpadBase import LaunchpadBase, _grid_note_classic

# The @Reimport marker is Live-specific: on script reimport, only
# __init__.py is re-executed and other modules stay cached. With this
# marker Live re-runs the import, so edits to SkinMK1.py take effect
# without restarting Live. It is a no-op outside Live (e.g. pytest).
from .SkinMK1 import make_skin  # @Reimport


class LP_MK1(LaunchpadBase):
	"""Classic Launchpad (and S / Mini): non-RGB, 123-layout (row*16+col)."""

	# all model flags stay False: this is the classic layout/skin
	# (_mk2_rgb = _mk3_rgb = _lpx = False, inherited from LaunchpadBase)

	# hardware-specific configuration, consumed by LaunchpadBase._build_controls()
	_side_notes = (8, 24, 40, 56, 72, 88, 104, 120)
	_drum_notes = (41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 89, 90, 91, 92, 93, 94, 95, 105, 106, 107)
	_grid_note = staticmethod(_grid_note_classic)
	_top_button_cc_base = 104
	_side_button_midi_type = MIDI_NOTE_TYPE

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self._skin = make_skin()
		self._build_controls()
		self.log_message("LaunchPad95 (classic) Loaded !")

	def _send_challenge(self):
		# mk1's challenge: 4 CC bytes on channel 0
		for index in range(4):
			challenge_byte = self._challenge >> 8 * index & 127
			self._send_midi((176, 17 + index, challenge_byte))

	def handle_sysex(self, midi_bytes):
		if len(midi_bytes) == 8 and midi_bytes[1:5] == (0, 32, 41, 6):
			response = int(midi_bytes[5])
			response += int(midi_bytes[6]) << 8
			if response == Live.Application.encrypt_challenge2(self._challenge):
				self.log_message("Challenge Response ok (mk1)")
				self._suppress_send_midi = False
				self.set_enabled(True)
		else:
			ControlSurface.handle_sysex(self, midi_bytes)
