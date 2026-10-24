"""Type stub for ``Live.Device`` (type-checking only).

``Parameter`` is declared here because the script never references it by
module path — it only uses instances obtained from ``device.parameters`` /
``mixer_device.sends`` etc.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from Live.Chain import Chain


class DeviceType:
    instrument = 0
    effect = 1
    drum = 2


class Parameter:
    """A Live device parameter (the thing controls map to)."""

    @property
    def name(self) -> str:
        ...

    @name.setter
    def name(self, value: str) -> None:
        ...

    @property
    def min(self) -> float:
        ...

    @property
    def max(self) -> float:
        ...

    @property
    def value(self) -> float:
        ...

    @value.setter
    def value(self, new_value: float) -> None:
        ...

    @property
    def is_enabled(self) -> bool:
        ...

    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        ...

    @property
    def default_value(self) -> float:
        ...

    @default_value.setter
    def default_value(self, value: float) -> None:
        ...

    def begin_gesture(self) -> None:
        ...

    def end_gesture(self) -> None:
        ...

    def add_value_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_value_listener(self, callback: Callable[..., None]) -> None: ...
    def value_has_listener(self, callback: Callable[..., None]) -> bool: ...


class DeviceView:
    """The device's view object (chain/pad selection)."""

    @property
    def selected_chain(self) -> Optional[Chain]:
        ...

    @selected_chain.setter
    def selected_chain(self, value: Optional[Chain]) -> None:
        ...

    @property
    def selected_drum_pad(self) -> Optional[Chain]:
        ...

    @selected_drum_pad.setter
    def selected_drum_pad(self, value: Optional[Chain]) -> None:
        ...


class Device:
    """A Live device (synth, effect, rack, ...)."""

    canonical_parent: object
    type: int  # DeviceType.*

    @property
    def name(self) -> str:
        ...

    @name.setter
    def name(self, value: str) -> None:
        ...

    @property
    def parameters(self) -> List[Parameter]:
        ...

    @parameters.setter
    def parameters(self, value: List[Parameter]) -> None:
        ...

    @property
    def chains(self) -> List[Chain]:
        ...

    @chains.setter
    def chains(self, value: List[Chain]) -> None:
        ...

    @property
    def drum_pads(self) -> List[Chain]:
        ...

    @property
    def can_have_drum_pads(self) -> bool:
        ...

    @property
    def can_have_chains(self) -> bool:
        ...

    @property
    def has_drum_pads(self) -> bool:
        ...

    @property
    def has_macro_mappings(self) -> bool:
        ...

    @has_macro_mappings.setter
    def has_macro_mappings(self, value: bool) -> None:
        ...

    @property
    def view(self) -> DeviceView:
        ...

    # -- subject listeners -------------------------------------------------
    def add_name_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_name_listener(self, callback: Callable[..., None]) -> None: ...
    def name_has_listener(self, callback: Callable[..., None]) -> bool: ...
    def add_parameters_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_parameters_listener(self, callback: Callable[..., None]) -> None: ...
    def parameters_has_listener(self, callback: Callable[..., None]) -> bool: ...
    def add_chains_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_chains_listener(self, callback: Callable[..., None]) -> None: ...
    def chains_has_listener(self, callback: Callable[..., None]) -> bool: ...
    def add_has_macro_mappings_listener(self, callback: Callable[..., None]) -> None: ...
    def remove_has_macro_mappings_listener(self, callback: Callable[..., None]) -> None: ...
    def has_macro_mappings_has_listener(self, callback: Callable[..., None]) -> bool: ...
