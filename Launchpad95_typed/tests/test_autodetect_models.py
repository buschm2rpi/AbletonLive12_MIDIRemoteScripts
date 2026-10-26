"""Auto-detecting Launchpad: flag -> hardware configuration mapping.

The legacy auto-detect entry point (``Launchpad``) identifies the connected
model from the challenge response (``handle_sysex``) and maps the model
flags onto the hardware-specific configuration attributes consumed by
``LaunchpadBase._build_controls()`` (``Launchpad.init()``). The ``surface``
fixture drives that path directly: it sets the model flag and calls
``init()``. These tests pin the mapping for all four models.
"""

import pytest

from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from Launchpad95_typed.LaunchpadBase import (
    _grid_note_classic,
    _grid_note_rgb,
)
from Launchpad95_typed.SkinMK1 import make_skin as make_skin_mk1
from Launchpad95_typed.SkinMK2 import make_skin as make_skin_mk2


# model -> (skin factory, side notes, drum notes, grid note, top CC base,
#           side button midi type)
CONFIG = {
    "mk1": (
        make_skin_mk1,
        (8, 24, 40, 56, 72, 88, 104, 120),
        (41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 89, 90, 91, 92, 93, 94, 95, 105, 106, 107),
        _grid_note_classic,
        104,
        MIDI_NOTE_TYPE,
    ),
    "mk2": (
        make_skin_mk2,
        (89, 79, 69, 59, 49, 39, 29, 19),
        (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126),
        _grid_note_rgb,
        104,
        MIDI_NOTE_TYPE,
    ),
    "mk3": (
        make_skin_mk2,
        (89, 79, 69, 59, 49, 39, 29, 19),
        (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126),
        _grid_note_rgb,
        91,
        MIDI_CC_TYPE,
    ),
    "lpx": (
        make_skin_mk2,
        (89, 79, 69, 59, 49, 39, 29, 19),
        (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126),
        _grid_note_rgb,
        91,
        MIDI_CC_TYPE,
    ),
}


@pytest.mark.parametrize("surface", ["mk1", "mk2", "mk3", "lpx"], indirect=["surface"])
def test_init_maps_detected_model_to_hardware_config(surface, request):
    skin_factory, side_notes, drum_notes, grid_note, top_cc, side_type = CONFIG[request.node.callspec.params["surface"]]
    # init() builds the skin (not just selects the factory): compare the
    # constructed skin's color table against the expected factory's output
    assert dict(surface._skin.iteritems()) == dict(skin_factory().iteritems())
    assert surface._side_notes == side_notes
    assert surface._drum_notes == drum_notes
    assert surface._grid_note is grid_note
    assert surface._top_button_cc_base == top_cc
    assert surface._side_button_midi_type == side_type


@pytest.mark.parametrize("surface", ["mk1", "mk2", "mk3", "lpx"], indirect=["surface"])
def test_init_builds_controls_for_detected_model(surface, request):
    _, side_notes, _, grid_note, top_cc, side_type = CONFIG[request.node.callspec.params["surface"]]
    matrix = surface._selector._matrix
    for row in range(8):
        for col in range(8):
            assert matrix.get_button(col, row).message_identifier() == grid_note(row, col)
    top_buttons = surface._selector._nav_buttons + surface._selector._mode_buttons
    for index, button in enumerate(top_buttons):
        assert button.message_identifier() == top_cc + index
        assert button.message_type() == MIDI_CC_TYPE
    for index, button in enumerate(surface._selector._side_buttons):
        assert button.message_identifier() == side_notes[index]
        assert button.message_type() == side_type
