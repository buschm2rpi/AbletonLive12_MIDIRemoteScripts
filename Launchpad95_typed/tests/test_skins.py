"""Skin color-mapping tests (Step 4).

Two palettes exist: ``SkinMK1`` (legacy 7-colour Launchpad) and ``SkinMK2``
(RGB MK2/MK3/LPX). ``make_skin()`` flattens the nested ``Colors`` class
hierarchy into a flat ``Skin`` mapping of dotted keys (``"Mode.Session.On"``
-> ``Color``), which is what the production components look up at runtime.

Coverage:
- Every key in a curated list (the color keys the code references, grouped
  by the plan's categories) resolves in **both** skins.
- Spot-check values: the two palettes differ.
- ``skin["Bogus.Key"]`` raises ``SkinColorMissingError``.
- Static cross-check: regex-scan the production ``.py`` files (excluding
  ``tests/``) for string literals passed to the skin-key setters and assert
  each dotted key resolves in both skins.

Scanner notes:
- A single-string ``set_on_off_values("X")`` expands to ``X.On`` / ``X.Off``
  (see ``ConfigurableButtonElement.set_on_off_values``).
- Calls with non-literal arguments (``"Mode." + mode1 + ".On"``,
  ``"StepSequencer.NoteEditor.Velocity" + str(i)``, variables, ints) are
  out of scope for a literal scan.
- Commented-out calls are also scanned (plain regex); the keys they
  reference (``Zooming.Selected`` / ``Zooming.Stopped``) resolve in both
  skins, so this is harmless.
- Two production typos are pinned as ``KNOWN_MISSING``: the anti-goals
  forbid editing production files in Phase 3, so the test asserts the
  missing set equals exactly those — any *new* unresolved key fails it.
"""

import os
import re

import pytest

from Launchpad95_typed.ColorsMK1 import Rgb as RgbMK1
from Launchpad95_typed.ColorsMK2 import Rgb as RgbMK2
from Launchpad95_typed.ConfigurableButtonElement import SkinColorMissingError
from Launchpad95_typed.SkinMK1 import make_skin as make_skin_mk1
from Launchpad95_typed.SkinMK2 import make_skin as make_skin_mk2

# The production package directory (parent of this tests/ directory).
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Curated key list (plan categories)
# ---------------------------------------------------------------------------

MODE_BUTTONS = (
    "Session",
    "ProSession",
    "Note",
    "Drum",
    "Device",
    "StepSequencer",
    "StepSequencer2",
    "User",
    "User2",
    "Mixer",
)

CURATED_KEYS = (
    {"DefaultButton." + s for s in ("On", "Off", "Disabled")}
    | {"Mode." + m + "." + s for m in MODE_BUTTONS for s in ("On", "Off")}
    | {
        "Session." + s
        for s in (
            "ClipStarted",
            "ClipStopped",
            "ClipRecording",
            "ClipEmpty",
            "ClipTriggeredPlay",
            "ClipTriggeredRecord",
        )
    }
    | {
        "ProSession." + s
        for s in (
            "On",
            "Off",
            "ClipStarted",
            "ClipTriggeredPlay",
            "ClipStopped",
            "ClipFoldedTrack",
            "ClipUnFoldedTrack",
        )
    }
    | {
        "ProSession." + m + "." + s
        for m in (
            "Shift",
            "Click",
            "Undo",
            "Delete",
            "Duplicate",
            "Double",
            "Quantize",
            "SessionRec",
            "SessionRecMode",
        )
        for s in ("On", "Off")
    }
    | {
        "Scale." + m + "." + s
        for m in ("AbsoluteRoot", "Horizontal", "Mode", "Key", "Octave",
                  "Modus", "QuickScale")
        for s in ("On", "Off")
    }
    | {"Scale.CircleOfFifths", "Scale.RelativeScale"}
    | {"QuickScale.NoteRepeater." + s for s in ("On", "Off")}
    | {
        "QuickScale.Quant." + s
        for s in (
            "On",
            "Off",
            "Mode",
            "Straight",
            "Swing",
            "Dotted",
            "Flam",
            "Selected",
            "Note",
            "Tripplet",
        )
    }
)

# ---------------------------------------------------------------------------
# Static scanner (production .py files, excluding tests/)
# ---------------------------------------------------------------------------

SETTERS = (
    "set_on_off_values",
    "set_light",
    "set_triggered_to_play_value",
    "set_stopped_value",
    "set_started_value",
    "set_empty_value",
    "set_selected_value",
)

_STRING_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')


def _balanced_arg_text(text, open_paren_index):
    """Text between the paren at ``open_paren_index`` and its match."""
    depth = 0
    quote = None
    for i in range(open_paren_index, len(text)):
        c = text[i]
        if quote:
            if c == quote and text[i - 1] != "\\":
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren_index + 1 : i]
    return None


def _split_top_level(args_text):
    """Split an argument list on top-level commas (string-aware)."""
    parts, cur, depth, quote = [], [], 0, None
    for i, c in enumerate(args_text):
        if quote:
            cur.append(c)
            if c == quote and args_text[i - 1] != "\\":
                quote = None
        elif c in "\"'":
            quote = c
            cur.append(c)
        elif c in "([":
            depth += 1
            cur.append(c)
        elif c in ")]":
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur))
    return [p.strip() for p in parts]


def _string_value(arg):
    """The string content of a string literal, else None."""
    match = _STRING_RE.fullmatch(arg)
    if match is None:
        return None
    return match.group(1) if match.group(1) is not None else match.group(2)


def _keys_from_args(setter, args_text):
    """Skin keys referenced by one call's string-literal arguments."""
    parts = _split_top_level(args_text)
    strings = [v for v in (_string_value(p) for p in parts) if v is not None]
    if not strings:
        return []
    if setter == "set_on_off_values" and len(parts) == 1:
        # set_on_off_values("X") -> states X.On / X.Off
        return [strings[0] + ".On", strings[0] + ".Off"]
    return strings


def scan_project():
    """Map each skin key to its sorted (file, line, setter) references.

    Scans every ``.py`` file under ``Launchpad95_typed/`` except ``tests/``.
    """
    references = {}
    for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):
        dirnames[:] = [d for d in dirnames if d not in ("tests", "__pycache__")]
        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                text = f.read()
            rel = os.path.relpath(os.path.join(dirpath, name), PROJECT_DIR)
            for setter in SETTERS:
                for match in re.finditer(re.escape(setter) + r"\s*\(", text):
                    args = _balanced_arg_text(text, match.end() - 1)
                    if args is None:
                        continue
                    keys = _keys_from_args(setter, args)
                    if not keys:
                        continue
                    line = text.count("\n", 0, match.start()) + 1
                    for key in keys:
                        references.setdefault(key, []).append((rel, line, setter))
    return {key: sorted(refs) for key, refs in references.items()}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def skin_mk1():
    # A built Skin is stateless; module scope keeps the suite fast.
    return make_skin_mk1()


@pytest.fixture(scope="module")
def skin_mk2():
    return make_skin_mk2()


@pytest.fixture(scope="module")
def scanned_references():
    return scan_project()


def _resolves(skin, key):
    try:
        skin[key]
        return True
    except SkinColorMissingError:
        return False


# ---------------------------------------------------------------------------
# Curated key resolution
# ---------------------------------------------------------------------------


def test_curated_key_count():
    # Pins the curation itself (plan's category list).
    assert len(CURATED_KEYS) == 82


@pytest.mark.parametrize("key", sorted(CURATED_KEYS))
def test_curated_key_resolves_in_both_skins(key, skin_mk1, skin_mk2):
    for skin in (skin_mk1, skin_mk2):
        value = skin[key]  # raises SkinColorMissingError if absent
        assert 0 <= int(value) <= 127


# ---------------------------------------------------------------------------
# Spot-check values (the two palettes differ)
# ---------------------------------------------------------------------------


def test_mk1_session_clip_started_is_green(skin_mk1):
    assert skin_mk1["Session.ClipStarted"] == RgbMK1.GREEN
    assert int(skin_mk1["Session.ClipStarted"]) == 52


def test_mk2_palette(skin_mk2):
    # The plan's "ProSession.On == Rgb.MINT" means the *mode button* color
    # (Mode.ProSession.On); the top-level ProSession.On (zoom-in session) is
    # Rgb.GREEN in the MK2 palette.
    assert skin_mk2["Mode.ProSession.On"] == RgbMK2.MINT
    assert int(skin_mk2["Mode.ProSession.On"]) == 29
    assert skin_mk2["Mode.Device.On"] == RgbMK2.PURPLE
    assert int(skin_mk2["Mode.Device.On"]) == 48
    # The Step 4 draft of the plan said StepSequencer2.On == Rgb.PINK; the
    # actual palette has Mode.StepSequencer2.On == Rgb.AMBER (Rgb.PINK is
    # Mode.StepSequencer.On).
    assert skin_mk2["Mode.StepSequencer2.On"] == RgbMK2.AMBER
    assert int(skin_mk2["Mode.StepSequencer2.On"]) == 9


def test_palettes_differ(skin_mk1, skin_mk2):
    # Same key, different palettes: the session mode button.
    assert int(skin_mk1["Mode.Session.On"]) != int(skin_mk2["Mode.Session.On"])


# ---------------------------------------------------------------------------
# Missing keys
# ---------------------------------------------------------------------------


def test_bogus_key_raises_skin_color_missing(skin_mk1, skin_mk2):
    with pytest.raises(SkinColorMissingError):
        skin_mk1["Bogus.Key"]
    with pytest.raises(SkinColorMissingError):
        skin_mk2["Bogus.Key"]


# ---------------------------------------------------------------------------
# Static cross-check: production code references vs. both palettes
# ---------------------------------------------------------------------------

KNOWN_MISSING = {
    # Production typo "DefaultButton.Disable" (StepSequencerComponent.py:842,
    # set_light) — should be "DefaultButton.Disabled". At runtime the skin
    # lookup misses and falls back to the boolean path.
    "DefaultButton.Disable",
    # Production typo "DefaultButton.Disaled" (StepSequencerComponent2.py:860,
    # single-arg set_on_off_values expands to .On/.Off).
    "DefaultButton.Disaled.On",
    "DefaultButton.Disaled.Off",
}


def test_scan_finds_expected_keys(scanned_references):
    # Sanity: the scanner is not silently broken.
    assert len(scanned_references) >= 100
    for key in (
        "DefaultButton.Disabled",
        "Mode.Session.On",
        "Session.ClipStarted",
        "Scale.Key.On",
        "Zooming.Selected",  # from a commented-out call; still scanned
    ):
        assert key in scanned_references


def test_scanned_keys_resolve_in_both_skins(scanned_references, skin_mk1, skin_mk2):
    missing = {
        key: refs
        for key, refs in scanned_references.items()
        if not _resolves(skin_mk1, key) or not _resolves(skin_mk2, key)
    }

    details = []
    for key in sorted(set(missing) - KNOWN_MISSING):
        locations = ", ".join(
            "%s:%d (%s)" % (ref[0], ref[1], ref[2]) for ref in missing[key]
        )
        details.append("missing from a palette: %s <- %s" % (key, locations))
    for key in sorted(KNOWN_MISSING - set(missing)):
        details.append("pinned typo now resolves (unpin it): %s" % key)
    assert not details, "\n".join(details)
