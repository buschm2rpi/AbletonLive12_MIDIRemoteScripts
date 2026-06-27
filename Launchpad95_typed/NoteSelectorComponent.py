from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

if TYPE_CHECKING:
    pass


# Allows to note selection and navigation through note groups and pages
class NoteSelectorComponent(ControlSurfaceComponent):
    def __init__(
        self,
        step_sequencer: Any,
        offset_buttons: tuple[ButtonElement, ...],
        control_surface: Any,
    ) -> None:
        self._step_sequencer = step_sequencer
        self._control_surface = control_surface
        ControlSurfaceComponent.__init__(self)
        self.set_enabled(False)

        self._clip: Optional[Any] = None
        self._track: Optional[Any] = None
        self._notes: Optional[Any] = None
        self._playhead: Optional[int] = None  # index of the playing position

        # First note for the 16 offset buttons
        self._root_note: int = 36
        # Relative offset selected button [0-15]
        self._offset: int = 0
        self._key: int = 0
        self._scale: list[int] = [0, 2, 4, 5, 7, 9, 11, 12]  # Major
        self._force: bool = True
        self._up_button: Optional[ButtonElement] = None
        self._down_button: Optional[ButtonElement] = None

        self._offset_buttons = offset_buttons
        self._enable_offset_button: bool = True  # self._mode == STEPSEQ_MODE_NORMAL
        # cache to optimize display for offset buttons minimizing MIDI traffic
        self._cache: list[int] = [
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
        ]
        self._was_velocity_shifted: bool = False
        for button in self._offset_buttons:
            assert isinstance(button, ButtonElement)
            button.remove_value_listener(self.note_offset_button_value)
            button.add_value_listener(
                self.note_offset_button_value, identify_sender=True
            )

    def set_clip(self, clip: Optional[Any]) -> None:
        self._clip = clip

    def set_note_cache(self, note_cache: Any) -> None:
        self._note_cache = note_cache

    def set_playhead(self, playhead: Optional[int]) -> None:
        self._playhead = playhead
        self._update_matrix()

    @property
    def _is_mute_shifted(self) -> bool:
        return self._step_sequencer._is_mute_shifted

    @property
    def _is_velocity_shifted(self) -> bool:
        return self._step_sequencer._is_velocity_shifted

    @property
    def _drum_group_device(self) -> Any:
        return self._step_sequencer._drum_group_device

    @property
    def is_drumrack(self) -> bool:
        return (
            self._step_sequencer._scale_selector.is_drumrack
            and self._drum_group_device is not None
        )

    @property
    def is_chromatic(self) -> bool:
        return self._step_sequencer._scale_selector.is_chromatic

    @property
    def is_diatonic(self) -> bool:
        return self._step_sequencer._scale_selector.is_diatonic

    # Updates the DOWN button light OK
    def _update_down_button(self) -> None:
        if self.is_enabled():
            if self._down_button is not None:
                if self._clip is None:
                    self._down_button.set_on_off_values(
                        "DefaultButton.Disabled", "DefaultButton.Disabled"
                    )
                    self._down_button.turn_off()
                else:
                    self._down_button.set_on_off_values(
                        "StepSequencer.Octave.On", "StepSequencer.Octave.Off"
                    )
                    if self.should_scroll():
                        if self.can_scroll_down():
                            self._down_button.turn_on()
                        else:
                            self._down_button.turn_off()
                    else:
                        if self.can_page_down():
                            self._down_button.turn_on()
                        else:
                            self._down_button.turn_off()

    # Refresh button and its listener OK
    def set_down_button(self, button: Optional[ButtonElement]) -> None:
        assert isinstance(button, (ButtonElement, type(None)))
        if self._down_button != button:
            if self._down_button is not None:
                self._down_button.remove_value_listener(self._down_button_value)
            self._down_button = button
            if self._down_button is not None:
                assert isinstance(button, ButtonElement)
                self._down_button.add_value_listener(
                    self._down_button_value, identify_sender=True
                )
            self._update_down_button()

    # Handle page and scroll displacement in down direction
    def _down_button_value(self, value: int, sender: ButtonElement) -> None:
        assert self._down_button is not None
        assert value in range(128)
        if self.is_enabled() and self._clip is not None:
            if value != 0 or not sender.is_momentary():
                if self.should_scroll():
                    self.scroll_down()
                else:
                    self.page_down()
                self._step_sequencer.update()

    # Updates the UP button light OK
    def _update_up_button(self) -> None:
        if self.is_enabled():
            if self._up_button is not None:
                if self._clip is None:
                    self._up_button.set_on_off_values(
                        "DefaultButton.Disabled", "DefaultButton.Disabled"
                    )
                    self._up_button.turn_off()
                else:
                    self._up_button.set_on_off_values(
                        "StepSequencer.Octave.On", "StepSequencer.Octave.Off"
                    )
                    if self.should_scroll():
                        if self.can_scroll_up():
                            self._up_button.turn_on()
                        else:
                            self._up_button.turn_off()
                    else:
                        if self.can_page_up():
                            self._up_button.turn_on()
                        else:
                            self._up_button.turn_off()

    # Refresh button and its listener OK
    def set_up_button(self, button: Optional[ButtonElement]) -> None:
        assert isinstance(button, (ButtonElement, type(None)))
        if self._up_button != button:
            if self._up_button is not None:
                self._up_button.remove_value_listener(self._up_button_value)
            self._up_button = button
            if self._up_button is not None:
                assert isinstance(button, ButtonElement)
                self._up_button.add_value_listener(
                    self._up_button_value, identify_sender=True
                )
            self._update_up_button()

    # Handle page and scroll displacement in up direction
    def _up_button_value(self, value: int, sender: ButtonElement) -> None:
        assert self._up_button is not None
        assert value in range(128)
        if self.is_enabled() and self._clip is not None:
            if value != 0 or not sender.is_momentary():  # If NOTEON or is Toggle
                # IF [mute_shift and NormalMode-> move(1)] [not mute_shift and MultinoteMode-> move(1)] ELSE move(12|16)_dependingIfdrumRack
                if self.should_scroll():
                    self.scroll_up()
                else:
                    self.page_up()
                self._step_sequencer.update()

    # Note Selector grid buttons listener (Normal Mode) and set view to the drum pad
    # Mute all the entries for a note (a lane)
    def note_offset_button_value(self, value: int, sender: ButtonElement) -> None:
        if (
            self.is_enabled() and value > 0 and self._enable_offset_button
        ):  # Is NoteON and Normal Mode
            if self._is_mute_shifted:
                try:
                    index = self._offset_buttons.index(sender)
                except ValueError:
                    index = -1
                self._step_sequencer._note_editor.mute_lane(self._root_note + index)
            else:
                try:
                    self._offset = self._offset_buttons.index(sender)
                except ValueError:
                    self._offset = -1
                if self.is_drumrack and self._drum_group_device is not None:
                    self._drum_group_device.view.selected_drum_pad = (
                        self._drum_group_device.drum_pads[self.selected_note]
                    )

                self._step_sequencer._scale_updated()

    def update(self) -> None:
        if self.is_enabled():
            self._step_sequencer._track_controller._do_implicit_arm(
                self._is_velocity_shifted and not self._step_sequencer._is_locked
            )
            if self._is_velocity_shifted and not self._step_sequencer._is_locked:
                self._control_surface.set_feedback_channels(
                    [11]
                )  # WHY USE Channel 12 to play the notes???
                self._control_surface._c_instance.set_feedback_velocity(
                    int(self._control_surface._skin["Note.Feedback"])
                )  # What is this???
                self._was_velocity_shifted = True
            elif self.is_drumrack and self._was_velocity_shifted:
                self._was_velocity_shifted = False
                self._offset = (
                    self._drum_group_device.view.selected_drum_pad.note
                    - self._root_note
                )
                self._step_sequencer._scale_updated()
            self._update_up_button()
            self._update_down_button()
            self._update_matrix()

    def _update_matrix(self) -> None:
        if self._enable_offset_button and self.is_enabled():
            for i in range(len(self._offset_buttons)):
                if self._clip is None:
                    self._offset_buttons[i].set_light("DefaultButton.Disabled")
                    self._offset_buttons[i].set_enabled(True)
                else:
                    note = self._root_note + i
                    if self.is_drumrack:
                        if self._drum_group_device.drum_pads[note].chains:
                            self._offset_buttons[i].set_on_off_values(
                                "DrumGroup.PadSelected", "DrumGroup.PadFilled"
                            )
                        else:
                            self._offset_buttons[i].set_on_off_values(
                                "DrumGroup.PadSelected", "DrumGroup.PadEmpty"
                            )
                    else:
                        if self._scale is not None:
                            if i % 12 == self._scale[0]:
                                self._offset_buttons[i].set_on_off_values(
                                    "StepSequencer.NoteSelector.Selected",
                                    "Note.Pads.Root",
                                )
                            elif i % 12 == self._scale[2] or i % 12 == self._scale[4]:
                                self._offset_buttons[i].set_on_off_values(
                                    "StepSequencer.NoteSelector.Selected",
                                    "Note.Pads.Highlight",
                                )
                            elif self._scale is not None and i % 12 in self._scale:
                                self._offset_buttons[i].set_on_off_values(
                                    "StepSequencer.NoteSelector.Selected",
                                    "Note.Pads.InScale",
                                )
                            else:
                                self._offset_buttons[i].set_on_off_values(
                                    "StepSequencer.NoteSelector.Selected",
                                    "Note.Pads.OutOfScale",
                                )
                        else:
                            self._offset_buttons[i].set_on_off_values(
                                "StepSequencer.NoteSelector.Selected",
                                "Note.Pads.OutOfScale",
                            )

                    if (
                        self._is_velocity_shifted
                        and not self._step_sequencer._is_locked
                    ):
                        # self._offset_buttons[i].force_next_send()
                        # self._offset_buttons[i].turn_off()
                        self._offset_buttons[i].set_enabled(False)
                        self._offset_buttons[i].set_channel(11)
                        self._offset_buttons[i].set_identifier(note)
                    else:
                        # self._offset_buttons[i].force_next_send()
                        self._offset_buttons[i].set_enabled(True)
                        self._offset_buttons[i].use_default_message()

                        if self._playhead is not None and self.note_is_playing(
                            self._clip, self._note_cache, note, self._playhead
                        ):
                            self._offset_buttons[i].set_on_off_values(
                                "StepSequencer.NoteSelector.Playing",
                                "StepSequencer.NoteSelector.Playing",
                            )

                    if self.selected_note == note:
                        if (
                            self._cache[i] != self._offset_buttons[i]._on_value
                            or self._force
                        ):
                            self._offset_buttons[i].turn_on()
                            self._cache[i] = self._offset_buttons[i]._on_value
                    else:
                        if (
                            self._cache[i] != self._offset_buttons[i]._off_value
                            or self._force
                        ):
                            self._offset_buttons[i].turn_off()
                            self._cache[i] = self._offset_buttons[i]._off_value
            self._force = False

    def set_enabled(self, enabled: bool) -> None:
        if enabled:
            self._cache = [
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
            ]
        ControlSurfaceComponent.set_enabled(self, enabled)

    def set_scale(self, scale: list[int], key: int = -1) -> None:
        if key != -1:
            self._key = key
        self._scale = scale
        # relativise scale
        for i in range(len(self._scale)):
            self._scale[i] = self._scale[i] - self._key

    # Is the cursor in the current button range and contain a note
    def note_is_playing(
        self, clip: Optional[Any], note_cache: Any, midi_note: int, playhead: int
    ) -> bool:
        if clip is not None and clip.is_playing and note_cache is not None:
            for note in note_cache:
                note_key = note[0]
                note_position = note[1]
                note_length = note[2]
                # note_velocity = note[3]
                note_muted = note[4]
                if (
                    midi_note == note_key
                    and note_position <= playhead
                    and note_position + note_length >= playhead
                    and not note_muted
                ):
                    return True
        return False

    def scroll_down(self) -> None:
        self.move(-1)

    def scroll_up(self) -> None:
        self.move(1)

    def page_down(self) -> None:
        if self.is_drumrack:
            self.move(-16)
        else:
            self.move(-12)

    def page_up(self) -> None:
        if self.is_drumrack:
            self.move(16)
        else:
            self.move(12)

    def can_scroll_down(self) -> bool:
        return self.can_move(-1)

    def can_scroll_up(self) -> bool:
        return self.can_move(1)

    def can_page_down(self) -> bool:
        if self.is_drumrack:
            return self.can_move(-16)
        else:
            return self.can_move(-12)

    def can_page_up(self) -> bool:
        if self.is_drumrack:
            return self.can_move(16)
        else:
            return self.can_move(12)

    # is in MIDI range
    def can_move(self, steps: int) -> bool:
        return self.selected_note + steps >= 0 and self.selected_note + steps < 128

    # Shifts the note selector up and down (12 if melodic instrument/16 if drumrack)
    def move(self, steps: int) -> None:
        if self.can_move(steps):
            if self.is_diatonic:
                # find the next note in scale in that direction
                octave = 0
                if steps > 0:
                    while self._offset + steps >= 12:
                        steps = steps - 12
                        octave = octave + 1
                    while steps != 0 and self._offset + steps not in self._scale:
                        steps = steps + 1
                        while self._offset + steps > 12:
                            steps = steps - 12
                            octave = octave + 1
                elif steps < 0:
                    while self._offset + steps < 0:
                        steps = steps + 12
                        octave = octave - 1
                    while steps != 0 and self._offset + steps not in self._scale:
                        steps = steps - 1
                        if self._offset + steps < 0:
                            steps = steps + 12
                            octave = octave - 1
                try:
                    idx = self._scale.index(self._offset + steps)
                except ValueError:
                    idx = -1
                self.set_selected_note(self._root_note + octave * 12 + self._scale[idx])
            else:
                self.set_selected_note(self._root_note + self._offset + steps)

    def set_selected_note(self, selected_note: int) -> None:
        if self.is_drumrack:
            self._root_note = int((selected_note + 12) / 16 - 1) * 16 + 4
            self._offset = (selected_note - self._root_note + 16) % 16
        else:
            self._root_note = int((selected_note - self._key) / 12) * 12 + self._key
            self._offset = (selected_note + 12 - self._root_note) % 12

        self._step_sequencer._scale_updated()

    def set_key(self, key: int) -> None:
        self._key = key

    def note_is_available(self, key: int) -> bool:  # deprecated???
        if self.is_drumrack:
            if self._drum_group_device.drum_pads[key].chains:
                return True
            else:
                return False
        else:
            for note in self._scale:
                if key % 12 == (self.root_note + note) % 12:
                    return True
                else:
                    return False
        return False

    def note_is_used(self, key: int) -> bool:  # deprecated???
        if self._clip is not None:
            for note in self._clip_notes:
                if note[0] == key:  # key: 0-127 MIDI note #
                    return True
        return False

    @property
    def selected_note(self) -> int:
        return self._root_note + self._offset

    def should_scroll(self) -> bool:
        return (
            not self._is_mute_shifted
            and not self._enable_offset_button
            or self._is_mute_shifted
            and self._enable_offset_button
        )

    # Used in Normal mode (Not Multinote) to delete/copy/mute/change loops regions
