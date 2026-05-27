# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: mappings.pyc (Python 3.11)

from Launchkey_MK4.mappings import create_launchkey_common_mappings

def create_mappings(control_surface):
    mappings = create_launchkey_common_mappings(control_surface)
    mappings['Transport'] = dict(play_toggle_button = 'play_button', play_pause_button = 'play_button_with_shift', capture_midi_button = 'record_button_with_shift')
    mappings['View_Control'] = dict(prev_track_button = 'track_left_button', next_track_button = 'track_right_button')
    return mappings
