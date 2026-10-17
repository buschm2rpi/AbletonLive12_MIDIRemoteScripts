"""ScaleComponent scale-computation tests (Step 3).

The component is constructed with the real surface (which provides both
``song()`` and ``show_message``) inside the surface's ``component_guard`` so
that the ``song`` / ``register_component`` dependencies resolve — exactly how
the production script constructs its components.
"""

import pytest

from Launchpad95_typed.ScaleComponent import (
    CIRCLE_OF_FIFTHS,
    ScaleComponent,
    TOP_OCTAVE,
)


@pytest.fixture
def scale(surface):
    with surface.component_guard():
        return ScaleComponent(control_surface=surface, enabled=True)


def major_index(scale):
    return scale._modus_names.index("Major")


# ---------------------------------------------------------------------------
# notes property
# ---------------------------------------------------------------------------

def test_notes_major_key0(scale):
    scale.set_modus(major_index(scale), message=False)
    scale.set_key(0, message=False)
    assert scale.notes == [0, 2, 4, 5, 7, 9, 11]


def test_notes_major_key4(scale):
    scale.set_modus(major_index(scale), message=False)
    scale.set_key(4, message=False)
    # Modus.scale transposes without wrapping (no mod 12).
    assert scale.notes == [4, 6, 8, 9, 11, 13, 15]


# ---------------------------------------------------------------------------
# Host sync
# ---------------------------------------------------------------------------

def test_set_key_syncs_root_note_and_message(scale, surface, host):
    scale.set_modus(major_index(scale), message=False)
    scale.set_key(4, message=True)
    assert surface.song().root_note == 4
    # KEY_NAMES[4] is "E" (C=0, C#=1, D=2, D#=3, E=4).
    assert host.messages[-1] == "Selected Scale: E Major"


def test_set_modus_syncs_scale_name_and_message(scale, surface, host):
    scale.set_key(0, message=False)
    scale.set_modus(major_index(scale), message=True)
    assert surface.song().scale_name == "Major"
    # Note the lowercase "selected scale:" — distinct from set_key's message.
    assert host.messages[-1] == "selected scale: C Major"


# ---------------------------------------------------------------------------
# Listener round-trips (Live-side changes flow back into the component)
# ---------------------------------------------------------------------------

def test_root_note_listener_round_trip(scale, surface):
    scale.set_key(0, message=False)
    song = surface.song()
    song.root_note = 5  # fires handle_root_note_changed (listener_called=True)
    assert scale._key == 5
    assert song.root_note == 5  # no write-back, no recursion


def test_scale_name_listener_round_trip(scale, surface):
    song = surface.song()
    # The fake song starts with scale_name == "Major"; a different value
    # fires handle_scale_name_changed.
    song.scale_name = "Natural Minor"
    assert scale._modus == scale._modus_names.index("Natural Minor")
    assert song.scale_name == "Natural Minor"


# ---------------------------------------------------------------------------
# Octave clamping
# ---------------------------------------------------------------------------

def test_top_octave_per_mode(scale):
    assert TOP_OCTAVE == {
        "chromatic_gtr": 7,
        "diatonic_ns": 2,
        "diatonic_chords": 7,
        "diatonic": 6,
        "chromatic": 7,
    }
    for mode, expected in TOP_OCTAVE.items():
        scale._mode = mode
        scale._set_top_octave(message=False)
        assert scale._top_octave == expected

    scale.set_drumrack(True)
    assert scale._top_octave == 8
    scale.set_drumrack(False)
    scale._mode = "diatonic"
    scale._set_top_octave(message=False)
    assert scale._top_octave == 6


def test_set_octave_rejects_out_of_range(scale):
    scale._mode = "diatonic"  # top octave 6
    scale._set_top_octave(message=False)
    scale._octave = 3

    scale.set_octave(5, message=False)
    assert scale._octave == 5
    scale.set_octave(6, message=False)  # == top octave -> rejected
    assert scale._octave == 5
    scale.set_octave(-1, message=False)  # < 0 -> rejected
    assert scale._octave == 5


def test_set_top_octave_clamps_current_octave(scale):
    scale._octave = 5
    scale._mode = "diatonic_ns"  # top octave 2
    scale._set_top_octave(message=False)
    assert scale._top_octave == 2
    assert scale._octave == 1


# ---------------------------------------------------------------------------
# get_pattern().note(x, y)
# ---------------------------------------------------------------------------

def test_pattern_note_fields(scale):
    scale.set_modus(major_index(scale), message=False)
    scale.set_key(0, message=False)
    scale._octave = 0
    pattern = scale.get_pattern()
    assert pattern.base_note == 12  # (octave + 1) * 12

    # Diatonic layout: index = x + 3y over the 7-note scale.
    # (x=0, y=0) -> scale index 0 -> note 0 (root)
    n = pattern.note(0, 0)
    assert n.index == 12
    assert n.root is True
    assert n.highlight is False
    assert n.in_scale is True
    assert n.valid is True

    # (x=0, y=1) -> scale index 3 -> note 5
    n = pattern.note(0, 1)
    assert n.index == 17
    assert n.root is False
    assert n.highlight is False
    assert n.in_scale is True

    # (x=2, y=0) -> scale index 2 -> note 4 (highlight: scale[2])
    n = pattern.note(2, 0)
    assert n.index == 16
    assert n.root is False
    assert n.highlight is True

    # (x=1, y=1) -> scale index 4 -> note 7 (highlight: scale[4])
    n = pattern.note(1, 1)
    assert n.index == 19
    assert n.highlight is True

    # (x=4, y=1) -> scale index 7 -> octave 1, note 0 (root again)
    n = pattern.note(4, 1)
    assert n.index == 24
    assert n.root is True
    assert n.in_scale is True
    assert n.valid is True


def test_pattern_base_note_follows_octave(scale):
    scale.set_modus(major_index(scale), message=False)
    scale.set_key(0, message=False)
    scale._octave = 2
    pattern = scale.get_pattern()
    assert pattern.base_note == 36  # (2 + 1) * 12
    assert pattern.note(0, 0).index == 36


# ---------------------------------------------------------------------------
# Mode buttons (matrix row 0)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("x", "mode", "interval", "horizontal"),
    [
        (2, "chromatic_gtr", 3, True),
        (3, "diatonic_ns", 3, True),
        (4, "diatonic_chords", 2, False),
        (5, "diatonic", 3, True),
        (6, "chromatic", 3, True),
    ],
)
def test_mode_buttons(scale, x, mode, interval, horizontal):
    scale._matrix_pressed(1, x, 0, True)
    assert scale._mode == mode
    assert scale._interval == interval
    assert scale._is_horizontal is horizontal
    assert scale.is_drumrack is False


def test_drumrack_mode_button(scale):
    scale._matrix_pressed(1, 7, 0, True)
    assert scale.is_drumrack is True


# ---------------------------------------------------------------------------
# Circle of fifths navigation
# ---------------------------------------------------------------------------

def test_circle_of_fifths_table():
    assert CIRCLE_OF_FIFTHS == [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]


def test_circle_of_fifths_forward(scale, surface):
    scale.set_key(0, message=False)  # C
    scale._matrix_pressed(1, 7, 2, True)  # (y=2, x=7): step forward -> G
    assert scale._key == 7
    assert surface.song().root_note == 7

    scale._matrix_pressed(1, 7, 2, True)  # G -> D
    assert scale._key == 2
    assert surface.song().root_note == 2


def test_circle_of_fifths_back(scale, surface):
    scale.set_key(7, message=False)  # G
    scale._matrix_pressed(1, 6, 1, True)  # (y=1, x=6): step back -> C
    assert scale._key == 0
    assert surface.song().root_note == 0
