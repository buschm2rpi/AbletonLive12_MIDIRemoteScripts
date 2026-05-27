# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: banking_util.pyc (Python 3.11)

from functools import partial
from ableton.v2.control_surface.parameter_slot_description import AND, CONDITION_NAME_KEY, CONDITIONS_LIST_NAME_KEY, DISPLAY_NAME_TRANSFORMER_KEY, OPERAND_NAME_KEY, PREDICATE_KEY, RESULTING_NAME_KEY
from ableton.v2.control_surface.parameter_slot_description import ParameterSlotDescription as ParameterSlotDescriptionBase
from ableton.v3.control_surface import DescribedDeviceParameterBank as DescribedDeviceParameterBankBase
from ableton.v3.control_surface import create_parameter_bank

def create_move_parameter_bank(device, banking_info):
    pass
# WARNING: Decompyle incomplete


class DescribedDeviceParameterBank(DescribedDeviceParameterBankBase):
    
    def set_shifted_state(self, state):
        for slot in self._dynamic_slots:
            if isinstance(slot, ParameterSlotDescription):
                slot.set_shifted_state(state)
            return None



class ParameterSlotDescription(ParameterSlotDescriptionBase):
    pass
# WARNING: Decompyle incomplete


def use(parameter_name):
    return ParameterSlotDescription().else_use(parameter_name)
