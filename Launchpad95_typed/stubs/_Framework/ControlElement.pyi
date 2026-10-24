"""Type stub for ``_Framework.ControlElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional


class ControlElement:
    """Base class of all control elements (buttons, sliders, ...)."""

    name: str
    canonical_parent: Any

    def __init__(self, name: str = "", resource_type: Any = None,
                 optimized_send_midi: Optional[bool] = None,
                 send_midi: Any = None, register_control: Any = None,
                 *a: Any, **k: Any) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def send_midi(self, message: bytes) -> None:
        ...

    def clear_send_cache(self) -> None:
        ...

    def reset(self) -> None:
        ...

    def reset_state(self) -> None:
        ...

    # Enabled-state API of the newer _Framework (absent from the
    # decompiled snapshot in this repo, present in current Live).
    def set_enabled(self, enable: bool) -> None:
        ...

    def is_enabled(self) -> bool:
        ...

    @property
    def resource(self) -> Any:
        ...
