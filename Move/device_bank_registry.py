# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: device_bank_registry.pyc (Python 3.11)

from ableton.v3.control_surface import DeviceBankRegistry as DeviceBankRegistryBase

class DeviceBankRegistry(DeviceBankRegistryBase):
    
    def clear_registry(self):
        self._device_bank_registry = { }
