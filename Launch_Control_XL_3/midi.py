# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: midi.pyc (Python 3.11)

from ableton.v3.control_surface.midi import SYSEX_END, SYSEX_START
SYSEX_HEADER = (SYSEX_START, 0, 32, 41, 2, 21)
SET_RELATIVE_ENCODER_MODES = ((182, 69, 127), (182, 72, 127), (182, 73, 127))

def make_connection_message(connect = (True,)):
    return SYSEX_HEADER + (2, 127 if connect else 0, SYSEX_END)


def make_enable_touch_output_message():
    return (182, 71, 127)

