from .LaunchpadBase import LaunchpadBase


class Launchpad(LaunchpadBase):
	"""Auto-detecting entry point (kept for backward compatibility).

	Detects the connected model at runtime from the challenge response
	(see ``LaunchpadBase.handle_sysex``) and defers full construction to
	``init()``. For statically configured models see ``LP_MK1`` / ``LP_MK2``
	/ ``LP_MK3`` / ``LP_X`` instead.
	"""
	pass
