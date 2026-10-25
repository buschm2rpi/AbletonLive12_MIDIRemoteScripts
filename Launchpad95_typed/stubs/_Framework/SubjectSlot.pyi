"""Type stub for ``_Framework.SubjectSlot`` (type-checking only).

The real ``Subject`` uses a metaclass that generates listener methods
(``add_<event>_listener`` / ``remove_<event>_listener`` /
``<event>_has_listener``) from ``__subject_events__``. Stubs cannot express
metaclass code-generation, so those methods are declared explicitly on the
concrete classes (see the ``Live`` stubs).
"""
from __future__ import annotations

from typing import Any, Callable


class Subject:
    """Base class of subject/slot model objects.

    Subclasses declare their events in ``__subject_events__`` (a tuple of
    event names or ``SubjectEvent`` tuples); the listener methods they
    expose are declared on the concrete stub classes.
    """

    __subject_events__: tuple

    def disconnect(self) -> None:
        ...


class SlotManager:
    """Mix-in managing SubjectSlot / SubjectSlotGroup registrations."""

    def register_slot(self, *a: Any, **k: Any) -> Any:
        """Register a slot; returns the SubjectSlot (set ``.subject`` to connect)."""
        ...

    def register_slot_manager(self) -> Any:
        """Register a slot group; returns the SubjectSlotGroup."""
        ...

    def disconnect(self) -> None:
        ...


def subject_slot(
    events: str, *a: Any, **k: Any
) -> Callable[[Callable[..., Any]], Any]:
    """Decorator: call the decorated method when the subject event fires."""
    ...


def subject_slot_group(
    event: str, *a: Any, **k: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: group listener over many subjects (sender is passed)."""
    ...
