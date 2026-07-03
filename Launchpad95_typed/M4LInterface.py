from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional  # noqa: F401

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

if TYPE_CHECKING:
    pass

_update_listener_type = Callable[[], None]  # type: Any


class M4LInterface(ControlSurfaceComponent):
    def __init__(self) -> None:
        ControlSurfaceComponent.__init__(self)
        self._name = "OSD"
        self._update_listener: Optional[_update_listener_type] = None
        self._updateML_listener: Optional[_update_listener_type] = None
        self.mode: str = " "
        self.info: list[str] = [" ", " "]
        self.attributes: list[str] = [" " for _ in range(8)]
        self.attribute_names: list[str] = [" " for _ in range(8)]
        self.clear()

    def disconnect(self) -> None:
        self._updateM4L_listener = None

    def set_mode(self, mode: str) -> None:
        self.clear()
        self.mode = mode

    def clear(self) -> None:
        self.info = [" ", " "]
        self.attributes = [" " for _ in range(8)]
        self.attribute_names = [" " for _ in range(8)]

    def set_update_listener(self, listener: _update_listener_type) -> None:
        self._update_listener = listener

    def remove_update_listener(self, listener: _update_listener_type) -> None:
        self._update_listener = None

    def update_has_listener(self) -> bool:
        return self._update_listener is not None

    @property
    def updateML(self) -> bool:
        return True

    def set_updateML_listener(self, listener: _update_listener_type) -> None:
        self._updateML_listener = listener

    def add_updateML_listener(self, listener: _update_listener_type) -> None:
        self._updateML_listener = listener

    def remove_updateML_listener(self, listener: _update_listener_type) -> None:
        self._updateML_listener = None

    def updateML_has_listener(self, listener: object) -> bool:
        return self._updateML_listener is not None

    def update(self, args: object = None) -> None:
        if self._updateML_listener is not None:
            self._updateML_listener()
