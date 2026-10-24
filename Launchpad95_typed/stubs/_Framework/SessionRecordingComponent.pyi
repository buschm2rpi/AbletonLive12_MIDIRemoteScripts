"""Type stub for ``_Framework.SessionRecordingComponent`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.ClipCreator import ClipCreator
from _Framework.CompoundComponent import CompoundComponent


class SessionRecordingComponent(CompoundComponent):
    """Session recording: record button, new scene/clip buttons, automation."""

    def __init__(self, clip_creator: Optional[ClipCreator] = None,
                 view_controller: Any = None, *a: Any, **k: Any) -> None:
        ...

    def set_record_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_automation_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_re_enable_automation_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_delete_automation_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_scene_list_new_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_new_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def set_new_scene_button(self, button: Optional[ButtonElement]) -> None:
        ...

    def deactivate_recording(self) -> None:
        ...

    def update(self) -> None:
        ...
