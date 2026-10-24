"""Type stub for ``_Framework.DeviceComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import Subject
from Live.Device import Device


class DeviceComponent(ControlSurfaceComponent, Subject):
    """Device parameter control: bank navigation, parameter mapping, locks."""

    def __init__(self, device_bank_registry: Any = None,
                 device_selection_follows_track_selection: bool = False,
                 *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def on_enabled_changed(self) -> None:
        ...

    def device(self) -> Optional[Device]:
        ...

    def set_device(self, device: Optional[Device]) -> None:
        ...

    def update_device_selection(self) -> None:
        ...

    def set_bank_prev_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_bank_next_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_bank_nav_buttons(self, down_button: Optional[ButtonElement],
                             up_button: Optional[ButtonElement]) -> None:
        ...

    def set_bank_buttons(self, buttons: Optional[Sequence[ButtonElement]]) -> None:
        ...

    def set_parameter_controls(self, controls: Optional[Sequence[Any]]) -> None:
        ...

    def set_lock_to_device(self, lock: bool, device: Device) -> None:
        ...

    def set_lock_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_on_off_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_lock_callback(self, callback: Optional[Callable[[], None]]) -> None:
        ...

    def restore_bank(self, bank_index: int) -> None:
        ...

    def device_name_data_source(self) -> Any:
        ...

    def update(self) -> None:
        ...
