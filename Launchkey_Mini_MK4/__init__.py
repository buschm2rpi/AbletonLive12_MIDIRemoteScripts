# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, SYNC, controller_id, inport, outport
from Launchkey_MK4.__init__ import LaunchkeyCommonControlSurface, create_launchkey_specification, midi
from elements import Elements
from mappings import create_mappings

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = [
                NOTES_CC]),
            inport(props = [
                NOTES_CC,
                SCRIPT]),
            outport(props = []),
            outport(props = [
                NOTES_CC,
                SYNC,
                SCRIPT])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 4661, product_ids = [
            321,
            322], model_name = [
            'Launchkey Mini MK4 25',
            'Launchkey Mini MK4 37']) }


def create_instance(c_instance):
    return Launchkey_Mini_MK4(specification = create_launchkey_specification(Elements, create_mappings, midi.MINI_MK4_SYSEX_HEADER), c_instance = c_instance)


class Launchkey_Mini_MK4(LaunchkeyCommonControlSurface):
    pass
