"""Type stub for ``_Framework.NotifyingControlElement`` (type-checking only).

A control element with the ``value`` subject event: listeners are called
with the received MIDI value. (The real class inherits the listener
methods from the ``Subject`` metaclass; they are declared here.)
"""
from __future__ import annotations

from typing import Any, Callable

from _Framework.ControlElement import ControlElement
from _Framework.SubjectSlot import Subject


class NotifyingControlElement(Subject, ControlElement):
    def add_value_listener(self, listener: Callable[..., Any],
                           *a: Any, **k: Any) -> None:
        ...

    def remove_value_listener(self, listener: Callable[..., Any],
                              *a: Any, **k: Any) -> None:
        ...

    def value_has_listener(self, listener: Callable[..., Any]) -> bool:
        ...

    def notify_value(self, value: Any) -> None:
        ...
