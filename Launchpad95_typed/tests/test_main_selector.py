"""MainSelectorComponent mode-transition tests (Step 2).

Uses the fully initialized ``surface`` fixture (default model: mk2).

Determinism: ``MainSelectorComponent._mode_value`` reads the wall clock
(``time.time()``) to implement the session button's < 500 ms long-press
pro-session toggle. The ``clock`` fixture replaces the module's ``time``
reference with a fake clock, and ``press_and_release`` holds each button for
600 ms by default so that a button-0 release never triggers the toggle
accidentally. No real sleeps anywhere.
"""

import pytest

from Launchpad95_typed import MainSelectorComponent as main_selector_module
from Launchpad95_typed.Settings import Settings

# mk2 mode buttons: top_buttons[4:] are CC 104+index on channel 0.
MODE_BUTTON_CCS = (108, 109, 110, 111)  # session, user1, user2, mixer


class FakeClock:
    """Stand-in for the ``time`` module: only ``time()`` is used."""

    def __init__(self, start=1000.0):
        self.now = start

    def time(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(main_selector_module, "time", fake)
    return fake


def last_cc_value(host, cc):
    """Last value sent as CC ``cc`` on channel 0, or None if never sent."""
    for message in reversed(host.midi_out):
        if len(message) == 3 and message[0] == 0xB0 and message[1] == cc:
            return message[2]
    return None


def press_and_release(sel, index, clock, hold_seconds=0.6):
    """Press then release mode button ``index``.

    Holds for >= 600 ms by default: a button-0 release within 500 ms of its
    press toggles pro-session mode, which would perturb tests that only care
    about plain mode switching.
    """
    button = sel._modes_buttons[index]
    button.receive_value(127)
    clock.advance(hold_seconds)
    button.receive_value(0)


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------

def test_channel_for_current_mode_table(surface):
    sel = surface._selector

    sel._main_mode_index = 0  # session
    assert sel.channel_for_current_mode() == 0

    sel._main_mode_index = 1  # user1: sub 0/1/2 -> 11/3/4
    for sub, expected in ((0, 11), (1, 3), (2, 4)):
        sel._sub_mode_list[1] = sub
        assert sel.channel_for_current_mode() == expected

    sel._main_mode_index = 2  # user2: sub 0/1/2 -> 1/2/5
    for sub, expected in ((0, 1), (1, 2), (2, 5)):
        sel._sub_mode_list[2] = sub
        assert sel.channel_for_current_mode() == expected


def test_channel_for_current_mode_mixer(surface):
    sel = surface._selector
    sel._main_mode_index = 3

    # sub_modes disabled (fresh surface is in session mode) -> mode() == 0
    assert sel._sub_modes.mode() == 0
    assert sel.channel_for_current_mode() == 6

    sel._sub_modes.set_enabled(True)  # on_enabled_changed resets to mode -1
    sel._sub_modes._mode_index = 2    # -> mode() == 3
    assert sel._sub_modes.mode() == 3
    assert sel.channel_for_current_mode() == 9


@pytest.mark.parametrize(
    ("user_mode", "expected"),
    [
        ("instrument", "Note"),
        ("device", "Device"),
        ("user 1", "User"),
        ("user 2", "User2"),
        ("drum stepseq", "StepSequencer"),
        ("melodic stepseq", "StepSequencer2"),
    ],
)
def test_get_skin_name(surface, user_mode, expected):
    assert surface._selector.getSkinName(user_mode) == expected


# ---------------------------------------------------------------------------
# Button-driven transitions
# ---------------------------------------------------------------------------

def test_press_sets_main_mode_index_and_button_states(surface, host, clock):
    sel = surface._selector
    for i in range(4):
        press_and_release(sel, i, clock)
        assert sel._main_mode_index == i
        for j in range(4):
            button = sel._modes_buttons[j]
            expected = int(button.on_value) if j == i else int(button.off_value)
            assert last_cc_value(host, MODE_BUTTON_CCS[j]) == expected


def test_user1_sub_mode_cycling(surface, clock):
    sel = surface._selector
    press_and_release(sel, 1, clock)
    assert sel._main_mode_index == 1
    assert sel._sub_mode_list[1] == 0
    assert Settings.USER_MODES_1[0] == "instrument"

    press_and_release(sel, 1, clock)  # re-press cycles to the next sub mode
    assert sel._sub_mode_list[1] == 1
    assert Settings.USER_MODES_1[1] == "device"

    press_and_release(sel, 1, clock)  # wraps around
    assert sel._sub_mode_list[1] == 0


def test_user2_sub_mode_cycling(surface, clock):
    sel = surface._selector
    press_and_release(sel, 2, clock)
    assert sel._main_mode_index == 2
    assert sel._sub_mode_list[2] == 0
    assert Settings.USER_MODES_2[0] == "drum stepseq"

    press_and_release(sel, 2, clock)
    assert sel._sub_mode_list[2] == 1
    assert Settings.USER_MODES_2[1] == "melodic stepseq"

    press_and_release(sel, 2, clock)
    assert sel._sub_mode_list[2] == 0


def test_mode_specific_host_messages(surface, host, clock):
    sel = surface._selector

    press_and_release(sel, 0, clock)
    assert host.messages[-1] == "SESSION MODE"

    press_and_release(sel, 3, clock)
    assert host.messages[-1] == "MIXER MODE"

    press_and_release(sel, 1, clock)  # user1 sub 0
    assert host.messages[-1] == "INSTRUMENT MODE"
    press_and_release(sel, 1, clock)  # user1 sub 1
    assert host.messages[-1] == "DEVICE CONTROLLER MODE"

    press_and_release(sel, 2, clock)  # user2 sub 0
    assert host.messages[-1] == "DRUM STEP SEQUENCER MODE"
    press_and_release(sel, 2, clock)  # user2 sub 1
    assert host.messages[-1] == "MELODIC SEQUENCER MODE"


def test_component_enablement(surface, clock):
    sel = surface._selector

    # Session mode (initial state): session on, mixer sub-modes off.
    assert sel._session.is_enabled() is True
    assert sel._sub_modes.is_enabled() is False

    # Mixer mode: sub-modes on. The session component is disabled by
    # ``_setup_session(False, ...)``, but ``DeprecatedSessionZoomingComponent
    # .update()`` (real framework, mirrored by the fake) re-enables it at the
    # end of every ``MainSelectorComponent.update()`` cycle, so the final
    # state is enabled — same as in real Live.
    press_and_release(sel, 3, clock)
    assert sel._sub_modes.is_enabled() is True
    assert sel._session.is_enabled() is True

    # The setup function itself expresses the intended enablement.
    sel._setup_session(False, True)
    assert sel._session.is_enabled() is False
    sel._setup_session(True, True)
    assert sel._session.is_enabled() is True

    press_and_release(sel, 0, clock)  # back to session
    assert sel._session.is_enabled() is True
    assert sel._sub_modes.is_enabled() is False


# ---------------------------------------------------------------------------
# Long-press pro-session toggle (session button)
# ---------------------------------------------------------------------------

def test_long_press_toggles_pro_session(surface, host, clock):
    sel = surface._selector
    assert sel._pro_session_on is False

    button = sel._modes_buttons[0]
    button.receive_value(127)
    clock.advance(0.2)  # 200 ms < 500 ms long-press threshold
    button.receive_value(0)

    assert sel._pro_session_on is True
    assert "PRO SESSION MODE" in host.messages

    # A second short press/release toggles back off.
    button.receive_value(127)
    clock.advance(0.2)
    button.receive_value(0)

    assert sel._pro_session_on is False
    assert host.messages[-1] == "SESSION MODE"


def test_long_press_threshold_not_met(surface, clock):
    """A release >= 500 ms after the press is a plain mode switch, no toggle."""
    sel = surface._selector
    assert sel._pro_session_on is False

    button = sel._modes_buttons[0]
    button.receive_value(127)
    clock.advance(0.6)  # 600 ms >= 500 ms threshold
    button.receive_value(0)

    assert sel._pro_session_on is False
    assert sel._main_mode_index == 0
