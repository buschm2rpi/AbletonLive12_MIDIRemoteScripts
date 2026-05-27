# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: device_navigation.pyc (Python 3.11)

from typing import NamedTuple
from Live.PluginDevice import PluginDevice
from Live.Track import Track
from ableton.v3.base import depends, find_if
from ableton.v3.control_surface.components import DeviceNavigationComponent as DeviceNavigateComponentBase
from ableton.v3.control_surface.components import FlattenedDeviceChain as FlattenedDeviceChainBase
from ableton.v3.control_surface.midi import CC_STATUS
from ableton.v3.live import is_device_rack, liveobj_valid
EE_PLUGIN_NAME = 'Ctrl-E'

def make_status_message(has_plugin):
    return (CC_STATUS, 53, 127 if has_plugin else 0)


def flatten_device_chain(track_or_chain):
    devices = []
    chain_devices = track_or_chain.devices if liveobj_valid(track_or_chain) else []
    for device in chain_devices:
        devices.append(device)
        if is_device_rack(device):
            for chain in device.chains:
                devices.extend(flatten_device_chain(chain))
                return devices


class FlattenedDeviceChain(FlattenedDeviceChainBase):
    
    def _update_devices(self, *_):
        self.items = flatten_device_chain(self._track)
        self._update_listeners()



class ObjectCache(NamedTuple):
    plugin: PluginDevice = 'ObjectCache'


class DeviceNavigationComponent(DeviceNavigateComponentBase):
    pass
# WARNING: Decompyle incomplete
