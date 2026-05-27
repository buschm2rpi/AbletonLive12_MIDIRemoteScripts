# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, PORTS_KEY, SCRIPT, controller_id, inport, outport
from Launch_Control_XL_3.device import DeviceComponent
from Launch_Control_XL_3.session_navigation import SessionNavigationComponent
from Launch_Control_XL_3.session_ring import SessionRingComponent
from  import midi
from display import display_specification
from elements import Elements
from mappings import create_mappings
from mixer import MixerComponent
from skin import Rgb, Skin

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(),
            inport(props = [
                SCRIPT]),
            outport(),
            outport(props = [
                SCRIPT])],
        4661: (lambda .0: [ 343 + i for i in .0 ])(vendor_id = range(8)(), product_ids = (lambda .0: [ 'LC3 {}'.format(i) for i in .0 ]), model_name = range(1, 9)()) }


def create_instance(c_instance):
    return Launch_Control_3(specification = Specification, c_instance = c_instance)


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin = Skin, colors = Rgb)
    link_session_ring_to_track_selection = True
    session_ring_component_type = SessionRingComponent
    create_mappings_function = create_mappings
    identity_response_id_bytes = (0, 32, 41, -1, 1, 0, 1)
    hello_messages = (midi.make_connection_message(),)
    goodbye_messages = (midi.make_connection_message(connect = False),)
    display_specification = display_specification
    component_map = {
        'Device': DeviceComponent,
        'Mixer': MixerComponent,
        'Session_Navigation': SessionNavigationComponent }


class Launch_Control_3(ControlSurface):
    pass
# WARNING: Decompyle incomplete
