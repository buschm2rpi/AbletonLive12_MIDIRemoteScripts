"""Static per-model classes (Phase 3 of plan_launchpad_base_refactor.md).

The four concrete classes ``LP_MK1`` / ``LP_MK2`` / ``LP_MK3`` / ``LP_X``
build everything eagerly in ``__init__`` (the model is known statically), so
unlike the auto-detecting ``Launchpad`` (``surface`` fixture) there is no
deferred construction: ``_init_done`` is already True right after the
constructor ran. The SYSEX handshake is kept as an *enable gate* only —
``_send_challenge`` emits just that model's probe and ``handle_sysex``
matches only its own response and enables the surface.

The ``static_surface`` fixture (tests/conftest.py) is parametrized over all
four models; tests branch on ``type(surface).__name__`` or pin one model with
``@pytest.mark.parametrize("static_surface", ["mk2"], indirect=True)``.
"""

import pytest

from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from Launchpad95_typed.LaunchpadBase import SYSEX_IDENTITY_REQUEST_MESSAGE
from Launchpad95_typed.MainSelectorComponent import MainSelectorComponent

# Small challenge that survives the 14-bit response encoding
# (response = lo + hi << 8, each a 7-bit SYSEX data byte) and the fake
# ``encrypt_challenge2`` (identity).
TEST_CHALLENGE = 0x1234


# --- model-specific expectations -------------------------------------------

# (mk2_rgb, mk3_rgb, lpx) — note MK3/LPX keep _mk2_rgb False (compat surface
# read by SpecialSessionComponent / SpecialProSessionComponent).
FLAGS = {
    "LP_MK1": (False, False, False),
    "LP_MK2": (True, False, False),
    "LP_MK3": (False, True, False),
    "LP_X": (False, False, True),
}

LOADED_MESSAGE = {
    "LP_MK1": "LaunchPad95 (classic) Loaded !",
    "LP_MK2": "LaunchPad95 (mk2) Loaded !",
    "LP_MK3": "LaunchPad95 (mk3) Loaded !",
    "LP_X": "LaunchPad95 (LPX) Loaded !",
}

# grid note layout: "classic" uses row*16+col, the RGB models the mk2 layout
GRID_NOTE = {
    "LP_MK1": lambda col, row: row * 16 + col,
    "LP_MK2": lambda col, row: (81 - 10 * row) + col,
    "LP_MK3": lambda col, row: (81 - 10 * row) + col,
    "LP_X": lambda col, row: (81 - 10 * row) + col,
}

# top buttons: CC 104+i (mk1/mk2) vs CC 91+i (mk3/lpx)
TOP_CC = {"LP_MK1": 104, "LP_MK2": 104, "LP_MK3": 91, "LP_X": 91}

# side buttons: NOTE (mk1/mk2) vs CC (mk3/lpx); note values per model
SIDE = {
    "LP_MK1": (MIDI_NOTE_TYPE, (8, 24, 40, 56, 72, 88, 104, 120)),
    "LP_MK2": (MIDI_NOTE_TYPE, (89, 79, 69, 59, 49, 39, 29, 19)),
    "LP_MK3": (MIDI_CC_TYPE, (89, 79, 69, 59, 49, 39, 29, 19)),
    "LP_X": (MIDI_CC_TYPE, (89, 79, 69, 59, 49, 39, 29, 19)),
}

# challenge probes each model's _send_challenge() must emit (bytes)
def _mk1_probe(challenge):
    return [
        bytes((176, 17 + index, challenge >> 8 * index & 127))
        for index in range(4)
    ]


def _mk2_probe(challenge):
    challenge_bytes = tuple(challenge >> 8 * index & 127 for index in range(4))
    return [bytes((240, 0, 32, 41, 2, 24, 64) + challenge_bytes + (247,))]


IDENTITY_PROBE = [bytes(SYSEX_IDENTITY_REQUEST_MESSAGE)]

PROBES = {
    "LP_MK1": _mk1_probe,
    "LP_MK2": _mk2_probe,
    "LP_MK3": lambda challenge: IDENTITY_PROBE,
    "LP_X": lambda challenge: IDENTITY_PROBE,
}

# valid challenge/identity responses per model
def _challenge_response(header):
    lo = TEST_CHALLENGE & 127
    hi = TEST_CHALLENGE >> 8 & 127
    return header + (lo, hi, 247)


RESPONSES = {
    "LP_MK1": _challenge_response((240, 0, 32, 41, 6)),
    "LP_MK2": _challenge_response((240, 0, 32, 41, 2, 24, 64)),
    "LP_MK3": (240, 126, 0, 6, 2, 0, 32, 41, 19, 1, 0, 0, 247),
    "LP_X": (240, 126, 0, 6, 2, 0, 32, 41, 3, 1, 0, 0, 247),
}

# a response that must NOT be accepted by each model (the other family's)
FOREIGN_RESPONSE = {
    "LP_MK1": RESPONSES["LP_MK2"],
    "LP_MK2": RESPONSES["LP_MK1"],
    "LP_MK3": RESPONSES["LP_X"],
    "LP_X": RESPONSES["LP_MK3"],
}

# quit SYSEX disconnect() must emit (None = none, classic sends none)
QUIT_SYSEX = {
    "LP_MK1": [],
    "LP_MK2": [bytes((240, 0, 32, 41, 2, 24, 64, 247))],
    "LP_MK3": [
        bytes((240, 0, 32, 41, 2, 13, 14, 0, 247)),
        bytes((240, 0, 32, 41, 2, 13, 16, 0, 247)),
    ],
    "LP_X": [
        bytes((240, 0, 32, 41, 2, 12, 14, 0, 247)),
        bytes((240, 0, 32, 41, 2, 12, 16, 0, 247)),
    ],
}

# programmer-mode SYSEX LP_MK3 / LP_X send upon a valid identity response
PROGRAMMER_SYSEX = {
    "LP_MK3": [
        bytes((240, 0, 32, 41, 2, 13, 14, 1, 247)),
        bytes((240, 0, 32, 41, 2, 13, 10, 0, 1, 247)),
        bytes((240, 0, 32, 41, 2, 13, 9, 1, 247)),
    ],
    "LP_X": [
        bytes((240, 0, 32, 41, 2, 12, 14, 1, 247)),
        bytes((240, 0, 32, 41, 2, 12, 10, 0, 1, 247)),
        bytes((240, 0, 32, 41, 2, 12, 9, 1, 247)),
    ],
}


def model(surface):
    return type(surface).__name__


# --- construction -----------------------------------------------------------

def test_eager_init_and_flags(static_surface):
    name = model(static_surface)
    mk2_rgb, mk3_rgb, lpx = FLAGS[name]
    assert static_surface._init_done is True
    assert isinstance(static_surface._selector, MainSelectorComponent)
    assert static_surface._mk2_rgb is mk2_rgb
    assert static_surface._mk3_rgb is mk3_rgb
    assert static_surface._lpx is lpx
    # flags are class-level (base __init__ must not shadow them with
    # instance attributes, or the subclasses' declarative flags break)
    assert "mk2_rgb" not in static_surface.__dict__
    assert "mk3_rgb" not in static_surface.__dict__
    assert "lpx" not in static_surface.__dict__


def test_loaded_message(static_surface, host):
    assert any(
        LOADED_MESSAGE[model(static_surface)] in m for m in host.messages
    )


def test_construction_emits_no_midi(static_surface, host):
    # eager init() runs while the base holds _suppress_send_midi: no LED or
    # handshake MIDI may leak during construction (fixture clears the flag
    # only after the constructor returned).
    assert host.midi_out == []


# --- layout -----------------------------------------------------------------

def test_grid_identifiers(static_surface):
    name = model(static_surface)
    matrix = static_surface._selector._matrix
    for row in range(8):
        for col in range(8):
            button = matrix.get_button(col, row)
            assert button.message_identifier() == GRID_NOTE[name](col, row)
            assert button.message_type() == MIDI_NOTE_TYPE


def test_top_buttons(static_surface):
    sel = static_surface._selector
    top_buttons = sel._nav_buttons + sel._mode_buttons
    for index, button in enumerate(top_buttons):
        assert button.message_identifier() == TOP_CC[model(static_surface)] + index
        assert button.message_type() == MIDI_CC_TYPE


def test_side_buttons(static_surface):
    msg_type, notes = SIDE[model(static_surface)]
    for index, button in enumerate(static_surface._selector._side_buttons):
        assert button.message_identifier() == notes[index]
        assert button.message_type() == msg_type


# --- handshake: probe -------------------------------------------------------

def test_send_challenge_emits_only_own_probe(static_surface, host):
    surface = static_surface
    surface._challenge = TEST_CHALLENGE
    surface._send_challenge()
    assert host.midi_out == PROBES[model(surface)](TEST_CHALLENGE)


# --- handshake: response ----------------------------------------------------

def test_valid_response_enables_surface(static_surface, host):
    surface = static_surface
    surface._challenge = TEST_CHALLENGE
    surface._update_hardware()
    assert surface._enabled is False
    surface.handle_sysex(RESPONSES[model(surface)])
    assert surface._enabled is True
    assert surface._suppress_send_midi is False


def test_valid_mk1_mk2_response_logs_challenge_ok(static_surface, host):
    surface = static_surface
    name = model(surface)
    if name in ("LP_MK3", "LP_X"):
        pytest.skip("identity-protocol models do not log a challenge")
    surface._challenge = TEST_CHALLENGE
    surface._update_hardware()
    surface.handle_sysex(RESPONSES[name])
    assert any("Challenge Response ok" in m for m in host.messages)


def test_valid_identity_response_sends_programmer_mode(static_surface, host):
    surface = static_surface
    name = model(surface)
    if name not in PROGRAMMER_SYSEX:
        pytest.skip("challenge-protocol models send no programmer mode")
    surface._update_hardware()
    surface.handle_sysex(RESPONSES[name])
    for message in PROGRAMMER_SYSEX[name]:
        assert message in host.midi_out


def test_foreign_response_does_not_enable(static_surface, host):
    surface = static_surface
    surface._update_hardware()
    surface.handle_sysex(FOREIGN_RESPONSE[model(surface)])
    assert surface._enabled is False


# --- disconnect -------------------------------------------------------------

def test_disconnect_sends_quit_sysex(static_surface, host):
    surface = static_surface
    surface.disconnect()
    for message in QUIT_SYSEX[model(surface)]:
        assert message in host.midi_out
    if not QUIT_SYSEX[model(surface)]:
        # classic: no Novation SYSEX at all on disconnect
        assert not any(m[0] == 240 for m in host.midi_out)
