"""Launchpad 95 for the Launchpad MK2.

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MK2
challenge is sent (sysex 240,0,32,41,2,24,64 + 4 bytes) and the validated
response enables MIDI out.
"""

import Live
from _Framework.ControlSurface import ControlSurface

from .LaunchpadBase import LaunchpadBase


class LP_MK2(LaunchpadBase):
	"""Launchpad MK2: RGB, mk2 grid layout (81-10*row+col)."""

	_mk2_rgb = True

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.init()

	def _send_challenge(self):
		# mk2 challenge: sysex with 4 challenge bytes
		challenge_bytes = tuple([ self._challenge >> 8 * index & 127 for index in range(4) ])
		self._send_midi((240, 0, 32, 41, 2, 24, 64) + challenge_bytes + (247,))

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
