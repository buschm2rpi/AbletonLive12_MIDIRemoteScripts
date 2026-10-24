"""Launchpad 95 for the Launchpad Mini MK3.

The model is known statically, so full construction happens eagerly in
``__init__`` and only the handshake remains as an enable gate: the MIDI
identity request is sent, and on the Mini MK3 identity response the script
switches the pad to programmer mode and enables MIDI out.
"""

from _Framework.ControlSurface import ControlSurface

from .LaunchpadBase import (
	LaunchpadBase,
	LP_MINI_MK3_FAMILY_CODE,
	LP_MINI_MK3_ID,
	SYSEX_END,
	SYSEX_IDENTITY_REQUEST_MESSAGE,
	STD_MSG_HEADER,
)


class LP_MK3(LaunchpadBase):
	"""Launchpad Mini MK3: RGB, mk2 grid layout, CC top/side buttons."""

	_mk3_rgb = True

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.init()

	def _send_challenge(self):
		# mk3 has no challenge: ask for the MIDI identity instead
		self._send_midi(SYSEX_IDENTITY_REQUEST_MESSAGE)

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
