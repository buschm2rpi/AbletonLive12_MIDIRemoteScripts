# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, controller_id, inport, outport
from active_parameter import ActiveParameterComponent
from colors import Rgb, Skin
from display import display_specification
from elements import Elements
from mappings import create_mappings
from midi import CONNECTION_MESSAGE, DISCONNECTION_MESSAGE
from mixer import MixerComponent
from mode_buttons import ModeButtonsComponent
from scene_launch import SceneLaunchComponent

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = [
                NOTES_CC]),
            inport(props = [
                NOTES_CC,
                SCRIPT]),
            outport(props = [
                NOTES_CC]),
            outport(props = [
                NOTES_CC,
                SCRIPT])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 7285, product_ids = [
            590,
            654,
            718], model_name = [
            'KeyLab 49 mk3',
            'KeyLab 61 mk3',
            'KeyLab 88 mk3']) }


def create_instance(c_instance):
    return KeyLab_mk3(specification = Specification, c_instance = c_instance)


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin = Skin, colors = Rgb)
    num_tracks = 4
    num_scenes = 3
    link_session_ring_to_track_selection = True
    link_session_ring_to_scene_selection = True
    include_auto_arming = True
    identity_response_id_bytes = (0, 32, 107, 2, 0, 10)
    create_mappings_function = create_mappings
    hello_messages = (CONNECTION_MESSAGE,)
    goodbye_messages = (DISCONNECTION_MESSAGE,)
    parameter_bank_size = 16
    component_map = {
        'Active_Parameter': ActiveParameterComponent,
        'Mixer': MixerComponent,
        'Mode_Buttons': ModeButtonsComponent,
        'Scene_Launch': SceneLaunchComponent }
    display_specification = display_specification


class KeyLab_mk3(ControlSurface):
    pass
# WARNING: Decompyle incomplete
