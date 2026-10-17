"""Fake ``_Framework.SliderElement`` — clean-room re-implementation.

Mirrors the decompiled ``_Framework/SliderElement.py`` (intact); the map mode
comes from the fake ``.MidiMap`` module.
"""

from __future__ import annotations

from .EncoderElement import EncoderElement
from .InputControlElement import MIDI_NOTE_TYPE
from .MidiMap import MapMode


class SliderElement(EncoderElement):
    def __init__(self, msg_type, channel, identifier, *a, **k):
        super().__init__(msg_type, channel, identifier, *a, map_mode=MapMode.absolute, **k)
