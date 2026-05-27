# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: mappings.pyc (Python 3.11)


def create_mappings(_):
    mappings = { }
    mappings['Device'] = dict(parameter_controls = 'encoders')
    mappings['Drum_Group'] = dict(matrix = 'pads')
    mappings['Transport'] = dict(play_button = 'play_button', stop_button = 'stop_button')
    mappings['View_Based_Recording'] = dict(record_button = 'record_button')
    mappings['View_Control'] = dict(prev_track_button = 'prev_button', next_track_button = 'next_button')
    return mappings
