# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: control.pyc (Python 3.11)

from ableton.v3.control_surface.controls import MappedSensitivitySettingControl, is_internal_parameter
from ableton.v3.live import liveobj_valid

class ParameterControl(MappedSensitivitySettingControl):
    
    class State(MappedSensitivitySettingControl.State):
        pass
    # WARNING: Decompyle incomplete
