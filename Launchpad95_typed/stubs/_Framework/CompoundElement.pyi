"""Type stub for ``_Framework.CompoundElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List

from _Framework.ControlElement import ControlElement
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.SubjectSlot import SlotManager


class CompoundElement(NotifyingControlElement, SlotManager):
    """A control element made of nested control elements (e.g. a matrix)."""

    def __init__(self, *a: Any, **k: Any) -> None:
        ...

    def register_control_elements(self, *elements: ControlElement) -> None:
        ...

    def register_control_element(self, element: ControlElement) -> None:
        ...

    def unregister_control_elements(self, *elements: ControlElement) -> None:
        ...

    def unregister_control_element(self, element: ControlElement) -> None:
        ...

    def has_control_element(self, control: ControlElement) -> bool:
        ...

    def owns_control_element(self, element: ControlElement) -> bool:
        ...

    def owned_control_elements(self) -> List[ControlElement]:
        ...

    def nested_control_elements(self) -> List[ControlElement]:
        ...

    def reset(self) -> None:
        ...

    def reset_state(self) -> None:
        ...

    # Compound value listeners pass (value, sender).
    def add_value_listener(self, listener: Callable[..., Any],
                           *a: Any, **k: Any) -> None:
        ...

    def remove_value_listener(self, listener: Callable[..., Any],
                              *a: Any, **k: Any) -> None:
        ...
