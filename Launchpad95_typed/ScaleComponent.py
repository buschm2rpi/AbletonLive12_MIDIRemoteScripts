from __future__ import annotations
from typing import Any, List, Optional, Tuple

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
import Live

KEY_NAMES: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CIRCLE_OF_FIFTHS: List[int] = [7 * k % 12 for k in range(12)]
# KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]


MUSICAL_MODES: list[Tuple[str, list[int]]] = []
for name, notes in Live.Song.get_all_scales_ordered():
    MUSICAL_MODES.append((name, notes))

TOP_OCTAVE: dict = {
    "chromatic_gtr": 7,
    "diatonic_ns": 2,
    "diatonic_chords": 7,
    "diatonic": 6,
    "chromatic": 7,
}


class ScaleComponent(ControlSurfaceComponent):
    # matrix = control_matrix(PlayableControl)

    def __init__(
        self,
        control_surface: Any = None,
        enabled: bool = False,
        mode: str = "diatonic",
        *a: Any,
        **k: Any,
    ) -> None:
        self._layout_set: bool = False
        self._control_surface = control_surface
        self._osd: Any = None
        self._modus: int = 0
        self._key: int = 0
        self._octave: int = 3
        self._mode: str = mode  # diatonic
        self._is_drumrack: bool = False
        self._quick_scale: bool = False
        self._is_horizontal: bool = True
        self._is_absolute: bool = False
        self._interval: int = 3
        self._matrix: Any = None
        self._top_octave: int = 6

        # C  D  E  F  G  A  B
        self._white_notes_index: List[int] = [0, 2, 4, 5, 7, 9, 11]

        self._current_minor_mode: int = 1  # Natural
        self._minor_modes: List[int] = [1, 13, 14]  # Natural, Harmonic, Melodic

        super(ScaleComponent, self).__init__(*a, **k)
        self.set_enabled(enabled)

    def _remove_scale_listeners(self) -> None:
        try:
            self.song().remove_root_note_listener(self.handle_root_note_changed)
        except RuntimeError:
            pass
        try:
            self.song().remove_scale_name_listener(self.handle_scale_name_changed)
        except RuntimeError:
            pass

    def _register_scale_listeners(self) -> None:
        try:
            self.song().add_root_note_listener(self.handle_root_note_changed)
        except RuntimeError:
            pass
        try:
            self.song().add_scale_name_listener(self.handle_scale_name_changed)
        except RuntimeError:
            pass

    def handle_root_note_changed(self) -> None:
        self.set_key(self.song().root_note, False, True)
        self.update()

    def handle_scale_name_changed(self) -> None:
        self.set_modus(self._modus_names.index(self.song().scale_name), False, True)
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        ControlSurfaceComponent.set_enabled(self, enabled)
        if not enabled:
            self._remove_scale_listeners()
        else:
            self._register_scale_listeners()

    @property
    def notes(self) -> Any:
        return self.modus.scale(self._key).notes

    @property
    def modus(self) -> Modus:
        return self._modus_list[self._modus]

    def set_key(
        self, key: int, message: bool = True, listener_called: bool = False
    ) -> None:
        if key >= 0 and key <= 11:
            self._key = key % 12
            if not listener_called:
                self.song().root_note = self._key
            if message:
                self._control_surface.show_message(
                    str("Selected Scale: " + KEY_NAMES[self._key])
                    + " "
                    + str(self._modus_names[self._modus])
                )

    def set_octave(self, octave: int, message: bool = True) -> None:
        if octave >= 0 and octave < self._top_octave:
            self._octave = octave
            if message:
                self._control_surface.show_message("Selected octave: " + str(octave))

    def _set_top_octave(self, message: bool = True) -> None:
        if self.is_drumrack:
            self._top_octave = 8
        else:
            self._top_octave = TOP_OCTAVE[self._mode]

        if self._octave >= self._top_octave:
            self._octave = self._top_octave - 1
            if message:
                self._control_surface.show_message(
                    "Selected octave: " + str(self._octave)
                )

    def octave_up(self, message: bool = True) -> None:
        self.set_octave(self._octave + 1, message)

    def octave_down(self, message: bool = True) -> None:
        self.set_octave(self._octave - 1, message)

    def set_modus(
        self, index: int, message: bool = True, listener_called: bool = False
    ) -> None:
        if index > -1 and index < len(self._modus_list):
            self._modus = index
            if not listener_called:
                self.song().scale_name = self._modus_names[self._modus]
            if message:
                self._control_surface.show_message(
                    str("selected scale: " + KEY_NAMES[self._key])
                    + " "
                    + str(self._modus_names[self._modus])
                )

    def set_drumrack(self, drumrack: Any) -> None:
        self._is_drumrack = drumrack
        self._set_top_octave(True)

    # def set_matrix(self, matrix):
    # if not matrix or not self._layout_set:
    # self._matrix = matrix
    # #self._matrix.set_control_element(matrix)
    # for index, button in enumerate(self._matrix):
    # #button.set_playable(False)
    # self._layout_set = bool(matrix)
    # self.update()
    def set_matrix(self, matrix: Any) -> None:
        self._matrix = matrix
        if matrix:
            matrix.reset()
        if matrix != self._matrix:
            if self._matrix is not None:
                self._matrix.remove_value_listener(self._matrix_pressed)
        self._matrix = matrix
        if self._matrix is not None:
            self._matrix.add_value_listener(self._matrix_pressed)
        self.update()

    def set_osd(self, osd: Any) -> None:
        self._osd = osd

    def _update_OSD(self) -> None:
        if self._osd is not None:
            self._osd.attributes[0] = ""
            self._osd.attribute_names[0] = ""
            self._osd.attributes[1] = MUSICAL_MODES[self._modus * 2]
            self._osd.attribute_names[1] = "Scale"
            self._osd.attributes[2] = KEY_NAMES[self._key % 12]
            self._osd.attribute_names[2] = "Root Note"
            self._osd.attributes[3] = self._octave
            self._osd.attribute_names[3] = "Octave"
            self._osd.attributes[4] = " "
            self._osd.attribute_names[4] = " "
            self._osd.attributes[5] = " "
            self._osd.attribute_names[5] = " "
            self._osd.attributes[6] = " "
            self._osd.attribute_names[6] = " "
            self._osd.attributes[7] = " "
            self._osd.attribute_names[7] = " "
            self._osd.update()

    def update(self) -> None:
        if self.is_enabled() and self._matrix is not None:
            # self._control_surface.log_message("update scale: "+str(self._matrix))
            super(ScaleComponent, self).update()
            self._update_OSD()
            # for index, button in enumerate(self._matrix):
            for button, (col, row) in self._matrix.iterbuttons():
                # row, col = button.coordinate
                button.set_enabled(True)
                if row == 0:
                    if col == 0:
                        if self._is_absolute:
                            button.set_light("Scale.AbsoluteRoot.On")
                        else:
                            button.set_light("Scale.AbsoluteRoot.Off")
                    elif col == 1:
                        if self._is_horizontal:
                            button.set_light("Scale.Horizontal.On")
                        else:
                            button.set_light("Scale.Horizontal.Off")
                    elif col == 2:
                        if not self.is_drumrack and self._mode == "chromatic_gtr":
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")
                    elif col == 3:
                        if not self.is_drumrack and self._mode == "diatonic_ns":
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")
                    elif col == 4:
                        if not self.is_drumrack and self._mode == "diatonic_chords":
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")
                    elif col == 5:
                        if not self.is_drumrack and self._mode == "diatonic":
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")
                    elif col == 6:
                        if not self.is_drumrack and self._mode == "chromatic":
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")
                    elif col == 7:
                        if self.is_drumrack:
                            button.set_light("Scale.Mode.On")
                        else:
                            button.set_light("Scale.Mode.Off")

                elif row == 1:
                    if self.is_drumrack:
                        if col == 7:
                            if self._quick_scale:
                                button.set_light("Scale.QuickScale.On")
                            else:
                                button.set_light("Scale.QuickScale.Off")
                        else:
                            button.set_light("DefaultButton.Disabled")
                    else:
                        if col == 0 or col == 1 or col == 3 or col == 4 or col == 5:
                            if self._key == self._white_notes_index[col] + 1:
                                button.set_light("Scale.Key.On")
                            else:
                                button.set_light("Scale.Key.Off")
                        elif col == 2:
                            button.set_light("Scale.RelativeScale")
                        elif col == 6:
                            button.set_light("Scale.CircleOfFifths")
                        elif col == 7:
                            if self._quick_scale:
                                button.set_light("Scale.QuickScale.On")
                            else:
                                button.set_light("Scale.QuickScale.Off")
                elif row == 2:
                    if self.is_drumrack:
                        button.set_light("DefaultButton.Disabled")
                    else:
                        if col < 7:
                            if self._key == self._white_notes_index[col]:
                                button.set_light("Scale.Key.On")
                            else:
                                button.set_light("Scale.Key.Off")
                        else:
                            button.set_light("Scale.CircleOfFifths")
                elif row == 3:
                    if self._octave == col:
                        button.set_light("Scale.Octave.On")
                    else:
                        if col < self._top_octave:
                            button.set_light("Scale.Octave.Off")
                        else:
                            button.set_light("DefaultButton.Disabled")
                elif row == 4:
                    if self.is_drumrack:
                        button.set_light("DefaultButton.Disabled")
                    else:
                        if self._modus == col:
                            button.set_light("Scale.Modus.On")
                        else:
                            button.set_light("Scale.Modus.Off")
                elif row == 5:
                    if self.is_drumrack:
                        button.set_light("DefaultButton.Disabled")
                    else:
                        if self._modus == col + 8:
                            button.set_light("Scale.Modus.On")
                        else:
                            button.set_light("Scale.Modus.Off")
                elif row == 6:
                    if self.is_drumrack:
                        button.set_light("DefaultButton.Disabled")
                    else:
                        if self._modus == col + 16:
                            button.set_light("Scale.Modus.On")
                        else:
                            button.set_light("Scale.Modus.Off")
                elif row == 7:
                    if self.is_drumrack:
                        button.set_light("DefaultButton.Disabled")
                    else:
                        if col + 24 > len(self._modus_list):
                            button.set_light("DefaultButton.Disabled")
                        elif self._modus == col + 24:
                            button.set_light("Scale.Modus.On")
                        else:
                            button.set_light("Scale.Modus.Off")
                # button.set_enabled(False)
                # button.update()

    # @matrix.pressed
    def _matrix_pressed(self, value: int, x: int, y: int, is_momentary: bool) -> None:
        message: bool = True
        if self.is_enabled() and value > 0:
            # y, x = pad.coordinate
            # modes
            if y == 0:
                # SCALE MODE SELECTION LOGIC
                if not self.is_drumrack:
                    if x == 0:
                        self._is_absolute = not self._is_absolute
                        if self._is_absolute:
                            self._control_surface.show_message("absolute root")
                        else:
                            self._control_surface.show_message("relative root")
                    if x == 1:
                        if self.is_diatonic:
                            self._is_horizontal = not self._is_horizontal
                            if self._is_horizontal:
                                self._control_surface.show_message("Is Horizontal")
                            else:
                                self._control_surface.show_message("Is Vertical")
                if x == 2:
                    self._mode = "chromatic_gtr"
                    self._is_drumrack = False
                    self._interval = 3
                    self._is_horizontal = True
                    self._control_surface.show_message("mode: chromatic gtr")
                if x == 3:
                    self._mode = "diatonic_ns"
                    self._is_drumrack = False
                    self._interval = 3
                    self._is_horizontal = True
                    self._control_surface.show_message("mode: diatonic not staggered")
                if x == 4:
                    self._mode = "diatonic_chords"
                    self._is_drumrack = False
                    self._interval = 2
                    self._is_horizontal = False
                    self._control_surface.show_message(
                        "mode: diatonic vertical (chords)"
                    )
                if x == 5:
                    self._mode = "diatonic"
                    self._is_drumrack = False
                    self._interval = 3
                    self._is_horizontal = True
                    self._control_surface.show_message("mode: diatonic")
                if x == 6:
                    self._mode = "chromatic"
                    self._is_drumrack = False
                    self._interval = 3
                    self._is_horizontal = True
                    self._control_surface.show_message("mode: chromatic")
                if x == 7:
                    self.set_drumrack(True)
                    self._control_surface.show_message("mode: drumrack")
                self._set_top_octave(True)
            # ROOT/SCALE SELECTION LOGIC
            keys: List[str] = [
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
                "A",
                "A#",
                "B",
            ]
            # root note
            if not self.is_drumrack:
                root: int = -1
                selected_key: int = self._key
                selected_modus: int = self._modus
                if (y == 1 and x in [0, 1, 3, 4, 5]) or (y == 2 and x < 7):
                    root = [0, 2, 4, 5, 7, 9, 11, 12][x]
                    if y == 1:
                        root = root + 1

                # if root == selected_key:#alternate minor/major
                # 	if selected_modus==0:
                # 		selected_modus = self._current_minor_mode
                # 	elif selected_modus in [1,13,14]:
                # 		self._current_minor_mode = selected_modus
                # 		selected_modus = 0
                # 	elif selected_modus==11:
                # 		selected_modus = 12
                # 	elif selected_modus==12:
                # 		selected_modus = 11

                # nav circle of 5th right ->
                if y == 2 and x == 7:
                    root = CIRCLE_OF_FIFTHS[
                        (CIRCLE_OF_FIFTHS.index(selected_key) + 1 + 12) % 12
                    ]
                    self._control_surface.show_message(
                        "circle of 5ths -> "
                        + keys[selected_key]
                        + " "
                        + str(self._modus_names[selected_modus])
                        + " => "
                        + keys[root]
                        + " "
                        + str(self._modus_names[selected_modus])
                    )
                    message = False

                # nav circle of 5th left <-
                if y == 1 and x == 6:
                    root = CIRCLE_OF_FIFTHS[
                        (CIRCLE_OF_FIFTHS.index(selected_key) - 1 + 12) % 12
                    ]
                    self._control_surface.show_message(
                        "circle of 5ths <- "
                        + keys[selected_key]
                        + " "
                        + str(self._modus_names[selected_modus])
                        + " => "
                        + keys[root]
                        + " "
                        + str(self._modus_names[selected_modus])
                    )
                    message = False

                # relative major/minor scale
                if y == 1 and x == 2:
                    if self._modus == 0:  # Ionian Mode (Major)
                        selected_modus = self._current_minor_mode
                        root = CIRCLE_OF_FIFTHS[
                            (CIRCLE_OF_FIFTHS.index(selected_key) + 3) % 12
                        ]  # Jump up 3 steps in 5th Circle equals jumping a third minor down
                    elif self._modus in [
                        1,
                        13,
                        17,
                    ]:  # Natural (Aeolian), Harmonic, Melodic Minor
                        self._current_minor_mode = selected_modus
                        selected_modus = 0
                        root = CIRCLE_OF_FIFTHS[
                            (CIRCLE_OF_FIFTHS.index(selected_key) - 3 + 12) % 12
                        ]  # Jump down 3 steps in 5th Circle equals jumping a third minor up
                    elif self._modus == 11:  # Minor Pentatonic
                        selected_modus = 12
                        root = CIRCLE_OF_FIFTHS[
                            (CIRCLE_OF_FIFTHS.index(selected_key) - 3) % 12
                        ]
                    elif self._modus == 12:  # Major Pentatonic
                        selected_modus = 11
                        root = CIRCLE_OF_FIFTHS[
                            (CIRCLE_OF_FIFTHS.index(selected_key) + 3 + 12) % 12
                        ]
                    self._control_surface.show_message(
                        "Relative scale : "
                        + keys[root]
                        + " "
                        + str(self._modus_names[selected_modus])
                    )
                    message = False
                if root != -1:
                    self.set_modus(selected_modus, message)
                    self.set_key(root, message)
            # QuickScale
            if y == 1 and x == 7:  # and not self.is_drumrack:
                self._quick_scale = not self._quick_scale
                if self._quick_scale:
                    self._control_surface.show_message("Quick scale ON")
                else:
                    self._control_surface.show_message("Quick scale OFF")
            # octave
            if y == 3:
                self.set_octave(x)
                self._control_surface.show_message("octave : " + str(self._octave))
            # modus (Scale)
            if y > 3 and not self.is_drumrack:
                self.set_modus(((y - 4) * 8 + x), message)
                self._control_surface.show_message(
                    str("Selected Scale: " + KEY_NAMES[self._key])
                    + " "
                    + str(self._modus_names[self._modus])
                )
            self.update()

    # @matrix.released
    def matrix_release(self, pad: Any) -> None:
        pass
        # selected_drum_pad = self._coordinate_to_pad_map[pad.coordinate]
        # if selected_drum_pad in self._selected_pads:
        # 	self._selected_pads.remove(selected_drum_pad)
        # 	if not self._selected_pads:
        # 		self._update_control_from_script()
        # 	self.notify_pressed_pads()
        # self._update_led_feedback()

    @property
    def is_drumrack(self) -> bool:
        return self._is_drumrack

    @property
    def is_diatonic(self) -> bool:
        return not self.is_drumrack and (
            self._mode == "diatonic"
            or self._mode == "diatonic_ns"
            or self._mode == "diatonic_chords"
        )

    @property
    def is_chromatic(self) -> bool:
        return not self.is_drumrack and (
            self._mode == "chromatic" or self._mode == "chromatic_gtr"
        )

    @property
    def is_diatonic_ns(self) -> bool:
        return self._mode == "diatonic_ns"

    @property
    def is_chromatic_gtr(self) -> bool:
        return self._mode == "chromatic_gtr"

    @property
    def is_quick_scale(self) -> bool:
        return self._quick_scale

    def get_pattern(self) -> Any:
        notes = self.notes
        # origin
        if not self._is_absolute:
            origin: int = 0
        elif self.is_diatonic:
            origin = 0
            for k in range(len(notes)):
                if notes[k] >= 12:
                    origin = k - len(notes)
                    break
        else:
            origin = -notes[0]

        # interval
        if self._interval is None:
            interval: int = 8
        elif self.is_chromatic:
            interval = [0, 2, 4, 5, 7, 9, 10, 11][self._interval]
        else:
            interval = self._interval

        # layout
        if self._is_horizontal:
            steps: List[int] = [1, interval]
        else:
            steps = [interval, 1]
        origin_list: list[int] = [origin, 0] if self._is_horizontal else [0, origin]

        return MelodicPattern(
            steps=steps,
            scale=notes,
            origin=origin_list,
            base_note=(self._octave + 1) * 12,
            chromatic_mode=self.is_chromatic,
            chromatic_gtr_mode=self.is_chromatic_gtr,
            diatonic_ns_mode=self.is_diatonic_ns,
        )


class Scale(object):
    # Input vars: scale name, array of scale steps -> (ScaleName, ScaleSteps)
    def __init__(self, name: str, notes: Any, *a: Any, **k: Any) -> None:
        super(Scale, self).__init__(*a, **k)
        self.name = name
        self.notes = notes


class Modus(Scale):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(Modus, self).__init__(*a, **k)

    def scale(self, base_note: int) -> Scale:
        return Scale(KEY_NAMES[base_note], [base_note + x for x in self.notes])

    def scales(self, base_notes: Any) -> List[Scale]:
        return [self.scale(b) for b in base_notes]


class MelodicPattern(object):
    def __init__(
        self,
        steps: Optional[List[int]] = None,
        scale: Any = None,
        base_note: int = 0,
        origin: Optional[List[int]] = None,
        valid_notes: Any = None,
        chromatic_mode: bool = False,
        chromatic_gtr_mode: bool = False,
        diatonic_ns_mode: bool = False,
        *a: Any,
        **k: Any,
    ) -> None:
        super(MelodicPattern, self).__init__(*a, **k)
        if steps is None:
            steps = [0, 0]
        if scale is None:
            scale = range(12)
        if origin is None:
            origin = [0, 0]
        if valid_notes is None:
            valid_notes = range(128)
        self.steps = steps
        self.scale = scale
        self.base_note = base_note
        self.origin = origin
        self.valid_notes = valid_notes
        self.chromatic_mode = chromatic_mode
        self.chromatic_gtr_mode = chromatic_gtr_mode
        self.diatonic_ns_mode = diatonic_ns_mode

    class NoteInfo:
        def __init__(
            self,
            index: int,
            channel: int,
            root: bool = False,
            highlight: bool = False,
            in_scale: bool = False,
            valid: bool = False,
        ) -> None:
            self.index = index
            self.channel = channel
            self.root = root
            self.highlight = highlight
            self.in_scale = in_scale
            self.valid = valid

    @property
    def _extended_scale(self) -> Any:
        if self.chromatic_mode:
            first_note = self.scale[0]
            return range(first_note, first_note + 12)
        else:
            return self.scale

    def _octave_and_note(self, x: int, y: int) -> Tuple[int, int]:
        scale = self._extended_scale
        scale_size = len(scale)
        if self.chromatic_mode:
            self.steps[1] = 5
        else:
            if self.diatonic_ns_mode:
                self.steps[1] = scale_size
        index = self.steps[0] * (self.origin[0] + x) + self.steps[1] * (
            self.origin[1] + y
        )
        if self.chromatic_gtr_mode and y > 3:
            index = index - 1
        octave = int(index / scale_size)
        note = scale[index % scale_size]
        return (octave, note)

    def note(self, x: int, y: int) -> MelodicPattern.NoteInfo:
        octave, note = self._octave_and_note(x, y)
        index = (self.base_note + 12 * octave + note) % 128
        root = note == self.scale[0]
        highlight = note == self.scale[2] or note == self.scale[4]
        in_scale = note in self.scale
        valid = index in self.valid_notes
        return self.NoteInfo(
            index, x, root=root, highlight=highlight, in_scale=in_scale, valid=valid
        )
