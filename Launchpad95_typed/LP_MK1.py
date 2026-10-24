"""Launchpad 95 for the classic Launchpad (MK1: Launchpad / S / Mini).

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MK1
challenge is sent (4 CC bytes) and the validated response enables MIDI out.
"""

import Live
from _Framework.ControlSurface import ControlSurface

from .LaunchpadBase import LaunchpadBase


class LP_MK1(LaunchpadBase):
	"""Classic Launchpad (and S / Mini): non-RGB, 123-layout (row*16+col)."""

	# all model flags stay False: this is the classic layout/skin
	# (_mk2_rgb = _mk3_rgb = _lpx = False, inherited from LaunchpadBase)

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.init()

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
