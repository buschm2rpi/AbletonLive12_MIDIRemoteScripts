"""Fake ``_Framework.NotifyingControlElement`` — clean-room re-implementation.

Mirrors the decompiled ``_Framework/NotifyingControlElement.py`` (intact).
"""

from __future__ import annotations

from .ControlElement import ControlElement
from .SubjectSlot import Subject, SubjectEvent


class NotifyingControlElement(Subject, ControlElement):
    __subject_events__ = (
        SubjectEvent(
            name="value",
            doc="Called when the control element receives a MIDI value from the hardware",
        ),
    )
