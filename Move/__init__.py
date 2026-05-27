# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

import logging
import weakref
from functools import partial
from Live.Base import Timer
from ableton.v3.base import const, lazy_attribute, listens
from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, HIDDEN, NOTES_CC, PORTS_KEY, SCRIPT, SYNC, TYPE_KEY, controller_id, inport, outport
from ableton.v3.control_surface.components import GridResolutionComponent, PitchProvider, SequencerClip, SessionNavigationComponent
from ableton.v3.live import liveobj_valid
from  import midi
from auto_arm import AutoArmComponent
from clip_actions import ClipActionsComponent
from colors import Colors
from device import DeviceComponent
from device_bank_registry import DeviceBankRegistry
from device_navigation import DeviceNavigationComponent
from device_provider import DeviceProvider
from dialog import DialogComponent
from display import display_specification
from drum_group import DrumGroupComponent
from elements import Elements
from firmware import FirmwareComponent, ShutDownState
from instrument import InstrumentComponent, NoteLayout
from loop_length import LoopLengthComponent
from mappings import create_mappings
from note_repeat import NoteRepeatComponent, NoteRepeatModel
from notification_suppression import NotificationSuppressionComponent
from quantization import QuantizationComponent
from recording import RecordingComponent
from session import SessionComponent
from skin import Skin
from sliced_simpler import SlicedSimplerComponent
from step_sequence import DEFAULT_GRID_RESOLUTION_INDEX, GRID_RESOLUTIONS, StepSequenceComponent
from track_list import TrackListComponent
from transport import TransportComponent
from volume_parameters import VolumeParametersComponent
logger = logging.getLogger(__name__)
DUMMY_PITCH_PROVIDER = PitchProvider()
PITCH_PROVIDERS = {
    'drum': 'Drum_Group',
    'instrument': 'Instrument',
    'simpler': 'Sliced_Simpler' }

def get_capabilities():
    return {
        TYPE_KEY: 'move',
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = [
                HIDDEN,
                NOTES_CC,
                SCRIPT]),
            inport(props = [
                HIDDEN]),
            outport(props = [
                HIDDEN,
                NOTES_CC,
                SYNC,
                SCRIPT]),
            outport(props = [
                HIDDEN])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 10626, product_ids = [
            6488], model_name = 'Ableton Move') }


def create_instance(c_instance):
    return Move(specification = Specification, c_instance = c_instance)


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin = Skin, colors = Colors)
    num_tracks = 7
    num_scenes = 4
    include_returns = True
    right_align_non_player_tracks = True
    include_auto_arming = True
    feedback_channels = midi.NOTE_MODE_FEEDBACK_CHANNELS
    playing_feedback_velocity = Colors.GREEN.midi_value
    recording_feedback_velocity = Colors.RED.midi_value
    identity_response_id_bytes = midi.MANUFACTURER_ID + (88, 50, 1, 0)
    hello_messages = (midi.make_get_control_mode_message(),)
    goodbye_messages = (midi.make_shut_down_image_message(),)
    create_mappings_function = create_mappings
    device_provider_type = DeviceProvider
    auto_arm_component_type = AutoArmComponent
    component_map = {
        'Clip_Actions': ClipActionsComponent,
        'Device': DeviceComponent,
        'Device_Navigation': DeviceNavigationComponent,
        'Drum_Group': DrumGroupComponent,
        'Instrument': InstrumentComponent,
        'Loop_Length': LoopLengthComponent,
        'Note_Repeat': NoteRepeatComponent,
        'Notification_Suppression': NotificationSuppressionComponent,
        'Recording': RecordingComponent,
        'Session': SessionComponent,
        'Session_Navigation': partial(SessionNavigationComponent, respect_borders = True),
        'Sliced_Simpler': SlicedSimplerComponent,
        'Step_Sequence': StepSequenceComponent,
        'Transport': TransportComponent,
        'Track_List': TrackListComponent }
    display_specification = display_specification


def note_mode_for_track(track, instrument_finder):
    if liveobj_valid(track) and track.has_midi_input:
        if liveobj_valid(instrument_finder.drum_group):
            return 'drum'
        if None(instrument_finder.sliced_simpler):
            return 'simpler'
        return None


class Move(ControlSurface):
    pass
# WARNING: Decompyle incomplete
