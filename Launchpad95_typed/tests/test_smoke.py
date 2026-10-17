"""Smoke tests (Step 1): prove the whole fake stack end-to-end.

These run before any component-level tests: if the fake ``Live`` /
``_Framework`` environment, the two-stage surface construction, and the
mode-button input path all work, the suite has a sound foundation.

The ``surface`` fixture (tests/conftest.py) builds a fully initialized
mk2 Launchpad on a fresh fake host per test.
"""

from Launchpad95_typed.MainSelectorComponent import MainSelectorComponent


def test_create_instance_returns_launchpad(surface):
    assert type(surface).__name__ == "Launchpad"
    assert surface._init_done is True


def test_full_init_builds_selector(surface):
    assert isinstance(surface._selector, MainSelectorComponent)
    assert surface._selector.number_of_modes() == 8


def test_loaded_message(surface, host):
    # Emitted via ControlSurface.log_message, which prefixes the class name:
    # "(Launchpad) LaunchPad95 (mk2) Loaded !".
    assert any("LaunchPad95 (mk2) Loaded !" in m for m in host.messages)


def test_update_in_each_main_mode(surface):
    sel = surface._selector
    for i in range(4):
        button = sel._modes_buttons[i]
        button.receive_value(127)
        button.receive_value(0)
        assert sel._main_mode_index == i


def test_disconnect(surface):
    surface.disconnect()
