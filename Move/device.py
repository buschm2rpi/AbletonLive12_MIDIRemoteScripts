# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: device.pyc (Python 3.11)

from Live.DeviceParameter import AutomationState, DeviceParameter
from ableton.v3.base import clamp, depends, find_if, listenable_property, task
from ableton.v3.control_surface import ACTIVE_PARAMETER_TIMEOUT, ParameterInfo
from ableton.v3.control_surface.components import DeviceComponent as DeviceComponentBase
from ableton.v3.control_surface.components import DeviceParametersComponent
from ableton.v3.control_surface.controls import ButtonControl, LockableButtonControl, TouchControl, control_list
from ableton.v3.control_surface.display import Renderable
from ableton.v3.live import display_name, is_clip_new_recording, is_parameter_quantized, is_song_recording, liveobj_valid, parameter_owner
from banking_util import DescribedDeviceParameterBank, create_move_parameter_bank
from control import ParameterControl
from custom_bank_definitions import CUSTOM_BANK_DEFINITIONS, is_shifted_parameter_mapping
from elements import ENCODER_SENSITIVITY
from suppressible_action_button import suppress_immediate_release_action
ENCODER_SENSITIVITY_FACTOR = 0.1

def parameter_is_automatable(parameter):
    if liveobj_valid(parameter):
        pass
    return isinstance(parameter, DeviceParameter)


class ParametersComponent(Renderable, DeviceParametersComponent):
    pass
# WARNING: Decompyle incomplete


class DeviceComponent(DeviceComponentBase):
    pass
# WARNING: Decompyle incomplete
