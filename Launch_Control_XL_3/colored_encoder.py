# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: colored_encoder.pyc (Python 3.11)

from Live.Device import Device
from Live.MixerDevice import MixerDevice
from ableton.v2.control_surface import LiveObjectDecorator
from ableton.v3.control_surface.elements import EncoderElement
from ableton.v3.control_surface.midi import CC_STATUS
from colors import Rgb

def get_color_for_parameter(parameter):
    parent = parameter.canonical_parent
    if isinstance(parent, (Device, LiveObjectDecorator)):
        return Rgb.PURPLE
    if None(parent, MixerDevice):
        return Rgb.LIGHT_BLUE if parameter.name == 'Track Volume' else Rgb.TURQUOISE
    if None in parameter.name:
        return Rgb.YELLOW
    if None in parameter.name:
        return Rgb.TURQUOISE
    if None in parameter.name:
        return Rgb.ORANGE
    return None.WHITE


def get_color_for_pan_value(value):
    if 'R' in value:
        return Rgb.ORANGE
    if None in value:
        return Rgb.DARK_BLUE
    return None.WHITE_HALF


class ColoredEncoderElement(EncoderElement):
    pass
# WARNING: Decompyle incomplete

