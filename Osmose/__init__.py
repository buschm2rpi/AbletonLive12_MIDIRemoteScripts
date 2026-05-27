# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, controller_id, inport, outport
from  import midi
from device_navigation import DeviceNavigationComponent
from display import display_specification
from elements import CONTINUOUS_PARAMETER_SENSITIVITY, Elements
from mappings import create_mappings
from skin import Skin
from view_control import ViewControlComponent

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = []),
            inport(props = []),
            inport(props = []),
            inport(props = [
                NOTES_CC,
                SCRIPT]),
            outport(props = []),
            outport(props = []),
            outport(props = []),
            outport(props = [
                SCRIPT])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 11796, product_ids = [
            26,
            28], model_name = [
            'Osmose 49',
            'Osmose 61']) }


def create_instance(c_instance):
    return Osmose(specification = Specification, c_instance = c_instance)


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    create_mappings_function = create_mappings
    control_surface_skin = create_skin(skin = Skin)
    continuous_parameter_sensitivity = CONTINUOUS_PARAMETER_SENSITIVITY
    quantized_parameter_sensitivity = CONTINUOUS_PARAMETER_SENSITIVITY / 2
    include_auto_arming = True
    identity_request = midi.make_connection_message(True)
    custom_identity_response = midi.IDENTITY_RESPONSE
    goodbye_messages = (midi.make_connection_message(False),)
    display_specification = display_specification
    component_map = {
        'Device_Navigation': DeviceNavigationComponent,
        'View_Control': ViewControlComponent }


class OsmoseBase(ControlSurface):
    pass
# WARNING: Decompyle incomplete


class Osmose(OsmoseBase):
    pass
