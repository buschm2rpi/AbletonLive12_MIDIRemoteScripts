"""pytest bootstrap for the Launchpad95_typed test suite.

Completes the bootstrap started by the worktree-root ``conftest.py`` (which
pre-installs the fake ``Live`` / ``_Framework`` environment so that importing
this package — required because ``tests/__init__.py`` makes it a subpackage
— succeeds outside of Ableton Live). This file adds the daemon patch and the
``host`` / ``song`` / ``surface`` / ``static_surface`` fixtures.

Run from the worktree root:

    .venv/bin/python -m pytest Launchpad95_typed/tests/
"""

from __future__ import annotations

import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKTREE_ROOT = os.path.dirname(os.path.dirname(_TESTS_DIR))

for _path in (_TESTS_DIR, _WORKTREE_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from fakes import install_fake_environment  # noqa: E402

install_fake_environment()

import Launchpad95_typed.DeviceControllerStripProxy as _dcsp  # noqa: E402

# Test-only: during ``Launchpad.init()`` the device-controller strips spawn
# one background thread each (a plain ``threading.Thread`` wrapping
# ``DeviceControllerStripServer.run``, which loops ``while True`` until a
# "shutdown" queue item). As non-daemon threads they block interpreter
# shutdown after the suite. The daemon decision is made at ``start()`` time
# (``Thread._set_tstate_lock`` reads ``self.daemon``), so the proxy module's
# own ``Thread`` reference is swapped for a subclass that forces
# ``daemon = True``. This touches no production file.

class _DaemonThread(_dcsp.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True


_dcsp.Thread = _DaemonThread

import pytest  # noqa: E402


@pytest.fixture
def host():
    """A fake host object (c_instance) wired to a fresh fake song."""
    from fakes import FakeHostApi

    return FakeHostApi()


@pytest.fixture
def song():
    """A fresh fake Live song (8 tracks x 8 scenes by default)."""
    from fake_live import make_fake_song

    return make_fake_song()


@pytest.fixture
def surface(host, request):
    """A fully constructed Launchpad script wired to the fake host.

    ``create_instance`` runs only ``Launchpad.__init__`` (SYSEX challenge,
    ``_selector = None``); the full construction (skin, matrix,
    ``MainSelectorComponent``) happens in ``Launchpad.init()``, which Live
    normally triggers from the hardware's challenge response via
    ``handle_sysex``. Tests drive it directly: set the model flag, then call
    ``init()``.

    Default model is **mk2** (exercises the RGB color-table path). Where a
    specific model matters, parameterize::

        @pytest.mark.parametrize("surface", ["mk1", "mk2"], indirect=["surface"])
    """
    from Launchpad95_typed import create_instance

    s = create_instance(host)
    model = getattr(request, "param", "mk2")
    if model == "mk2":
        s._mk2_rgb = True
    elif model == "mk3":
        s._mk3_rgb = True
    elif model == "lpx":
        s._lpx = True
    # model == "mk1": no flag
    # ``handle_sysex`` (which the tests bypass) clears this flag right before
    # calling ``init()``; while set, ``Launchpad._send_midi`` drops every
    # message, so ``host.midi_out`` would stay empty.
    s._suppress_send_midi = False
    s.init()
    return s


@pytest.fixture(params=["mk1", "mk2", "mk3", "lpx"])
def static_surface(host, request):
    """A statically configured per-model script (LP_MK1 / LP_MK2 / LP_MK3 /
    LP_X), parametrized over all four models.

    Unlike the ``surface`` fixture (auto-detecting ``Launchpad``, whose full
    construction is deferred until the SYSEX handshake), the static classes
    build everything eagerly in ``__init__`` while ``_suppress_send_midi`` is
    still set: LED sends during construction are dropped *and* not cached, so
    ``host.midi_out`` stays empty until the test clears the flag — mirroring
    the real two-stage flow, where ``set_enabled(True)`` after the handshake
    pushes the initial LED state.

    The returned value is the constructed surface. Use
    ``type(surface).__name__`` (``LP_MK1`` / ``LP_MK2`` / ``LP_MK3`` /
    ``LP_X``) to branch on the model, or parametrize a single-model test with
    ``@pytest.mark.parametrize("static_surface", ["mk2"], indirect=True)``.
    """
    from Launchpad95_typed.LP_MK1 import LP_MK1
    from Launchpad95_typed.LP_MK2 import LP_MK2
    from Launchpad95_typed.LP_MK3 import LP_MK3
    from Launchpad95_typed.LP_X import LP_X

    classes = {"mk1": LP_MK1, "mk2": LP_MK2, "mk3": LP_MK3, "lpx": LP_X}
    cls = classes[request.param]
    s = cls(c_instance=host)
    # ``handle_sysex`` (which the tests bypass) clears this flag right before
    # enabling; while set, ``LaunchpadBase._send_midi`` drops every message,
    # so the tests clear it to observe probes/quit SYSEX on ``host.midi_out``.
    s._suppress_send_midi = False
    return s
