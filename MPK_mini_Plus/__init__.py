# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface import ControlSurfaceSpecification, create_control_surface
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, controller_id, inport, outport
from elements import Elements
from mappings import create_mappings

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = [
                SCRIPT,
                NOTES_CC]),
            outport(props = [
                SCRIPT])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 2536, product_ids = [
            84], model_name = [
            'MPK mini Plus']) }


def create_instance(c_instance):
    return create_control_surface(name = 'MPK_mini_Plus', specification = Specification, c_instance = c_instance)


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    identity_response_id_bytes = (71, 84, 0, 25)
    create_mappings_function = create_mappings
