# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from functools import partial
from ableton.v3.base import const, listens, task
from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, SYNC, controller_id, inport, outport
from ableton.v3.control_surface.components import DEFAULT_DRUM_TRANSLATION_CHANNEL, MixerComponent
from ableton.v3.live import liveobj_valid
from  import midi
from auto_arm import AutoArmComponent
from colors import Rgb
from cue_point import CuePointComponent
from display import default_label_content, display_specification
from drum_group import DrumGroupComponent
from elements import Elements
from encoder_touch import EncoderTouchComponent
from keyboard import KeyboardComponent
from mappings import create_mappings
from scale import ScaleComponent
from session import SessionComponent
from session_navigation import SessionNavigationComponent
from skin import Skin
from step_sequence import SequencerClip, StepSequenceComponent
from transport import TransportComponent
from zoom import ZoomComponent

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
            323,
            324,
            325,
            326], model_name = [
            'Launchkey MK4 25',
            'Launchkey MK4 37',
            'Launchkey MK4 49',
            'Launchkey MK4 61']) }


def create_instance(c_instance):
    return Launchkey_MK4(specification = create_launchkey_specification(Elements, create_mappings, midi.MK4_SYSEX_HEADER), c_instance = c_instance)


def create_launchkey_specification(elements_type, create_mappings_function, sysex_header):
    pass
# WARNING: Decompyle incomplete


def pitch_provider_for_track(track, instrument_finder):
    if liveobj_valid(track) and track.has_midi_input:
        if liveobj_valid(instrument_finder.drum_group):
            return 'Drum_Group'
        return None


class LaunchkeyCommonControlSurface(ControlSurface):
    pass
# WARNING: Decompyle incomplete


class Launchkey_MK4(LaunchkeyCommonControlSurface):
    pass
# WARNING: Decompyle incomplete
