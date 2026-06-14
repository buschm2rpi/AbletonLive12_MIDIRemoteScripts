from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from _Framework import Task
from _Framework.CompoundComponent import CompoundComponent

if TYPE_CHECKING:
	from Live.NoteRepeat import NoteRepeat

t = 3.0 / 2.0
NOTE_REPEAT_FREQUENCIES = [4, 4*t, 8, 8*t, 16, 16*t, 32, 32*t]
del t
QUANTIZATION_NAMES = ('1/4', '1/4t', '1/8',  '1/8t', '1/16', '1/16t', '1/32', '1/32t')

class DummyNoteRepeat(object):
    repeat_rate: float = 1.0
    enabled: bool = False


class NoteRepeatComponent(CompoundComponent):
    """
    Component for setting up the note repeat
    """

    def __init__(self, *a: Any, **k: Any) -> None:
        super(NoteRepeatComponent, self).__init__(*a, **k)
        self._last_record_quantization: Optional[Any] = None
        self._note_repeat: Optional[Any] = None
        self._freq_index: int = 2
        self.set_note_repeat(None)

    def on_enabled_changed(self) -> None:
        if self.is_enabled():
            self._enable_note_repeat()
        else:
            self._disable_note_repeat()

    def set_freq_index(self, index: int) -> None:
        self._freq_index = index
        self._update_note_repeat(self.is_enabled())

    def freq_index(self) -> int:
        return self._freq_index

    def freq_name(self) -> str:
        return QUANTIZATION_NAMES[self._freq_index]

    def update(self) -> None:
        super(NoteRepeatComponent, self).update()

    def set_select_buttons(self, buttons: Any) -> None:
        self._options.select_buttons.set_control_element(buttons)

    def set_note_repeat(self, note_repeat: Optional[Any]) -> None:
        if not note_repeat:
            note_repeat = DummyNoteRepeat()
        if self._note_repeat is not None:
            self._note_repeat.enabled = False
        self._note_repeat = note_repeat
        self._update_note_repeat(enabled=self.is_enabled())

    def set_pad_parameters(self, element: Optional[Any]) -> None:
        if element:
            element.reset()

    def _enable_note_repeat(self) -> None:
        self._last_record_quantization = self.song().midi_recording_quantization
        self._set_recording_quantization(False)
        self._update_note_repeat(enabled=True)

    def _disable_note_repeat(self) -> None:
        if not self.song().midi_recording_quantization and self._last_record_quantization:
            self._set_recording_quantization(self._last_record_quantization)
        self._update_note_repeat(enabled=False)

    def _set_recording_quantization(self, value: Any) -> None:
        def doit() -> None:
            self.song().midi_recording_quantization = value

        self._tasks.parent_task.add(Task.run(doit))

    def _on_selected_option_changed(self, option: int) -> None:
        frequency = NOTE_REPEAT_FREQUENCIES[option]
        self._note_repeat.repeat_rate = 1.0 / frequency * 4.0  # type: ignore[union-attr]

    def _update_note_repeat(self, enabled: bool = False) -> None:
        self._on_selected_option_changed(self._freq_index)
        self._note_repeat.enabled = self.is_enabled()  # type: ignore[union-attr]
