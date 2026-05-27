# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: device_provider.pyc (Python 3.11)

from ableton.v3.control_surface import DeviceProvider as DeviceProviderBase
from ableton.v3.live import is_instrument_rack

class DeviceProvider(DeviceProviderBase):
    can_skip_over_device_rack = (lambda device: if not device.can_have_drum_pads:
passis_instrument_rack(device))()
