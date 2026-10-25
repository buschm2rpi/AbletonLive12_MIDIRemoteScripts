"""Type stub for ``_Framework.CompoundComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, List, TypeVar

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

_ComponentT = TypeVar("_ComponentT", bound=ControlSurfaceComponent)

class CompoundComponent(ControlSurfaceComponent):
    """A component made of sub-components."""

    def __init__(self, *a: Any, **k: Any) -> None:
        ...

    def update_all(self) -> None:
        ...

    def register_component(self, component: _ComponentT) -> _ComponentT:
        ...

    def register_components(self, *components: ControlSurfaceComponent) -> List[ControlSurfaceComponent]:
        ...

    def has_component(self, component: ControlSurfaceComponent) -> bool:
        ...

    def set_enabled(self, enable: bool) -> None:
        ...

    def _set_enabled_recursive(self, enable: bool) -> None:
        ...

    def set_allow_update(self, allow_updates: bool) -> None:
        ...
