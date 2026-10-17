"""Assemble and install the fake ``Live`` + ``_Framework`` environment.

``install_fake_environment()`` makes the *unmodified* ``Launchpad95_typed``
code importable and runnable outside of Ableton Live:

1. Puts this directory (``tests/``) on ``sys.path`` so ``fake_core`` /
   ``fake_live`` / ``fake_framework`` are importable by absolute name.
2. Builds a fake ``Live`` module tree (``Live.Base``, ``Live.Song``,
   ``Live.Track``, ``Live.Application``, ``Live.MidiMap``, ...) from
   ``fake_live`` and installs it as ``sys.modules["Live"]``.
3. Aliases the ``fake_framework`` package (and every submodule) into
   ``sys.modules`` under the real ``_Framework`` / ``_Framework.*`` names.

After that, ``import Launchpad95_typed`` works: its ``import Live`` and
``from _Framework.X import Y`` statements resolve to the fakes.

The fake host object (``FakeHostApi``) is the single seam between the script
and the fake Live model; tests construct it (usually via the ``host`` fixture
in ``conftest.py``) and pass it to the script as ``c_instance``.
"""

from __future__ import annotations

import importlib
import os
import sys
import types

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _ensure_tests_on_path() -> None:
    if TESTS_DIR not in sys.path:
        sys.path.insert(0, TESTS_DIR)


def _make_module(name: str, **attrs) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__package__ = name
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


# ---------------------------------------------------------------------------
# Fake host object (Live.MidiRemoteScript / c_instance)
# ---------------------------------------------------------------------------


class FakeHostApi:
    """Fake of Ableton's host object — the single seam between script and Live.

    Records everything the script asks the host to do, so tests can assert on
    it (``messages``, ``midi_out``, ``session_highlights`` ...).
    """

    def __init__(self, song=None):
        from fake_live import make_fake_song

        self._song = song if song is not None else make_fake_song()
        self._application = None
        self._messages = []
        self._midi_out = []
        self._session_highlights = []
        self._pad_translations = None
        self._feedback_channels = None
        self._feedback_velocity = None
        self._controlled_track = None
        self._lock_toggles = 0
        self._rebuild_requests = 0
        self._instance_identifier = 1
        self._handle = 1

    # -- HostApi surface ---------------------------------------------------
    def song(self):
        return self._song

    def application(self):
        if self._application is None:
            from fake_live import Application

            self._application = Application.get_application()
        return self._application

    def send_midi(self, midi_bytes):
        self._midi_out.append(bytes(midi_bytes))

    def show_message(self, message):
        self._messages.append(message)

    def log_message(self, message):
        # Recorded alongside show_message so tests can assert on host-visible
        # output (e.g. the "LaunchPad95 (mk2) Loaded !" banner, which the
        # script emits via ControlSurface.log_message with a
        # "(Launchpad) " prefix).
        self._messages.append(message)

    def request_rebuild_midi_map(self):
        self._rebuild_requests += 1

    def set_pad_translation(self, translations):
        self._pad_translations = translations

    def set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        self._session_highlights.append((track_offset, scene_offset, width, height, include_return_tracks))

    def toggle_lock(self):
        self._lock_toggles += 1

    def update_locks(self):
        pass

    def set_feedback_channels(self, channels):
        self._feedback_channels = channels

    def set_feedback_velocity(self, velocity):
        self._feedback_velocity = velocity

    def set_controlled_track(self, track):
        self._controlled_track = track

    def release_controlled_track(self):
        self._controlled_track = None

    def instance_identifier(self):
        return self._instance_identifier

    def handle(self):
        return self._handle

    @property
    def note_repeat(self):
        return None

    # -- test introspection -------------------------------------------------
    @property
    def messages(self):
        return list(self._messages)

    @property
    def midi_out(self):
        return list(self._midi_out)

    @property
    def session_highlights(self):
        return list(self._session_highlights)

    @property
    def rebuild_request_count(self):
        return self._rebuild_requests

    @property
    def lock_toggle_count(self):
        return self._lock_toggles


# ---------------------------------------------------------------------------
# Fake Live module tree
# ---------------------------------------------------------------------------


def _build_live_module() -> types.ModuleType:
    import fake_live

    base = _make_module(
        "Live.Base",
        LimitationError=fake_live.LimitationError,
        log=fake_live.log,
    )
    application = _make_module(
        "Live.Application",
        Application=fake_live.Application,
        combine_apcs=fake_live.Application.combine_apcs,
        get_application=fake_live.Application.get_application,
        get_random_int=fake_live.Application.get_random_int,
        encrypt_challenge=fake_live.Application.encrypt_challenge,
        encrypt_challenge2=fake_live.Application.encrypt_challenge2,
    )
    song = _make_module(
        "Live.Song",
        Song=fake_live.Song,
        Quantization=fake_live.Quantization,
        RecordingQuantization=fake_live.RecordingQuantization,
        SessionRecordStatus=fake_live.SessionRecordStatus,
        CaptureMode=fake_live.CaptureMode,
        get_all_scales_ordered=fake_live.Song.get_all_scales_ordered,
    )
    track = _make_module("Live.Track", Track=fake_live.Track)
    rack_device = _make_module("Live.RackDevice", RackDevice=fake_live.RackDevice)
    device = _make_module("Live.Device", Device=fake_live.Device, DeviceType=fake_live.DeviceType)
    chain = _make_module("Live.Chain", Chain=fake_live.Chain)
    clip = _make_module("Live.Clip", Clip=fake_live.Clip)
    scene = _make_module("Live.Scene", Scene=fake_live.Scene)
    midi_map = _make_module(
        "Live.MidiMap",
        MapMode=fake_live.MapMode,
        NoteFeedbackRule=fake_live.NoteFeedbackRule,
        CCFeedbackRule=fake_live.CCFeedbackRule,
        PitchBendFeedbackRule=fake_live.PitchBendFeedbackRule,
        map_midi_note_with_feedback_map=fake_live.map_midi_note_with_feedback_map,
        map_midi_cc_with_feedback_map=fake_live.map_midi_cc_with_feedback_map,
        map_midi_pitchbend_with_feedback_map=fake_live.map_midi_pitchbend_with_feedback_map,
        send_feedback_for_parameter=fake_live.send_feedback_for_parameter,
        forward_midi_note=fake_live.forward_midi_note,
        forward_midi_cc=fake_live.forward_midi_cc,
        forward_midi_pitchbend=fake_live.forward_midi_pitchbend,
    )
    midi_remote_script = _make_module("Live.MidiRemoteScript", MidiRemoteScript=fake_live.MidiRemoteScript)

    live = _make_module(
        "Live",
        Base=base,
        Application=application,
        Song=song,
        Track=track,
        RackDevice=rack_device,
        Device=device,
        Chain=chain,
        Clip=clip,
        Scene=scene,
        MidiMap=midi_map,
        MidiRemoteScript=midi_remote_script,
    )
    live.__path__ = []  # mark as a package
    return live


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

_installed = False


def install_fake_environment() -> None:
    """Install the fake ``Live`` / ``_Framework`` modules (idempotent)."""
    global _installed
    if _installed:
        return

    _ensure_tests_on_path()

    # Fake Live tree.
    if "Live" not in sys.modules:
        sys.modules["Live"] = _build_live_module()
    for sub in ("Base", "Application", "Song", "Track", "RackDevice", "Device", "Chain", "Clip", "Scene", "MidiMap", "MidiRemoteScript"):
        sys.modules.setdefault("Live." + sub, getattr(sys.modules["Live"], sub))

    # Fake _Framework: alias the fake_framework package + all submodules.
    import fake_framework

    if "_Framework" not in sys.modules:
        sys.modules["_Framework"] = fake_framework
        for name in sorted(os.listdir(fake_framework.__path__[0])):
            if name.endswith(".py") and not name.startswith("__"):
                module_name = name[:-3]
                importlib.import_module("fake_framework." + module_name)
                sys.modules.setdefault("_Framework." + module_name, sys.modules["fake_framework." + module_name])

    _installed = True


def uninstall_fake_environment() -> None:
    """Remove the fake modules (mainly useful for test isolation)."""
    global _installed
    for name in list(sys.modules):
        if name == "Live" or name.startswith("Live.") or name == "_Framework" or name.startswith("_Framework."):
            del sys.modules[name]
    _installed = False
