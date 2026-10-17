"""Fake ``_Framework.MidiMap`` — re-exports the mapping primitives from ``fake_live``.

In real Live, ``MapMode`` / the feedback rules / the ``map_*`` + ``forward_*``
functions live in the host-provided ``Live.MidiMap`` module. The fake takes
them from ``tests/fake_live.py`` (same values, same no-op behavior), so that
the fake ``ButtonElement`` / ``EncoderElement`` / ``ControlSurface`` can import
them from ``.MidiMap`` without touching the real ``Live`` module.
"""

from fake_live import (  # noqa: F401
    CCFeedbackRule,
    MapMode,
    NoteFeedbackRule,
    PitchBendFeedbackRule,
    forward_midi_cc,
    forward_midi_note,
    forward_midi_pitchbend,
    map_midi_cc_with_feedback_map,
    map_midi_note_with_feedback_map,
    map_midi_pitchbend_with_feedback_map,
    send_feedback_for_parameter,
)
