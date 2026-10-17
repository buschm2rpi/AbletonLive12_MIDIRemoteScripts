"""Fake ``_Framework.SubjectSlot`` — re-exports from ``fake_core``."""

from fake_core import (  # noqa: F401
    CallableSlotMixin,
    CallableSubjectSlotGroup,
    MultiSubjectSlot,
    SlotManager,
    Subject,
    SubjectEvent,
    SubjectMeta,
    SubjectSlot,
    SubjectSlotError,
    SubjectSlotGroup,
    setup_subject,
    subject_add_event,
    subject_slot,
    subject_slot_group,
)
