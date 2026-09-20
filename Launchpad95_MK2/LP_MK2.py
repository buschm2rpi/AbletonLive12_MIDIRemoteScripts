import traceback

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from Launchpad95_typed.ConfigurableButtonElement import ConfigurableButtonElement
from Launchpad95_typed.LaunchpadBase import LaunchpadBase
from Launchpad95_typed.Log import log
from Launchpad95_typed.MainSelectorComponent import MainSelectorComponent
from Launchpad95_typed.M4LInterface import M4LInterface

from .SkinMK2 import make_skin
            
class LP_MK2(LaunchpadBase):

    def __init__(self, *a, **k):

        super().__init__(*a, **k)

        self._mk2_rgb = True
        self._skin = make_skin()
        self._side_notes = (89, 79, 69, 59, 49, 39, 29, 19)
        self._drum_notes = (20, 30, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126)

        with self.component_guard():
            is_momentary = True
            self._config_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 0, optimized_send_midi=False)
            self._config_button.add_value_listener(self._config_value)
            self._user_byte_write_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 16)
            self._user_byte_write_button.name = 'User_Byte_Button'
            self._user_byte_write_button.send_value(1)
            self._user_byte_write_button.add_value_listener(self._user_byte_value)
            matrix = ButtonMatrixElement()
            matrix.name = 'Button_Matrix'
            for row in range(8):
                button_row = []
                for column in range(8):
                    # for mk2 buttons are assigned "top to bottom"
                    midi_note = (81 - (10 * row)) + column
                    button = ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, midi_note, skin = self._skin, control_surface = self)
                    button.name = str(column) + '_Clip_' + str(row) + '_Button'
                    button_row.append(button)
                matrix.add_row(tuple(button_row))

            top_buttons = [ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, 104 + index, skin = self._skin) for index in range(8)]
            side_buttons = [ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, self._side_notes[index], skin = self._skin) for index in range(8)]
                
            top_buttons[0].name = 'Bank_Select_Up_Button'
            top_buttons[1].name = 'Bank_Select_Down_Button'
            top_buttons[2].name = 'Bank_Select_Left_Button'
            top_buttons[3].name = 'Bank_Select_Right_Button'
            top_buttons[4].name = 'Session_Button'
            top_buttons[5].name = 'User1_Button'
            top_buttons[6].name = 'User2_Button'
            top_buttons[7].name = 'Mixer_Button'
            side_buttons[0].name = 'Vol_Button'
            side_buttons[1].name = 'Pan_Button'
            side_buttons[2].name = 'SndA_Button'
            side_buttons[3].name = 'SndB_Button'
            side_buttons[4].name = 'Stop_Button'
            side_buttons[5].name = 'Trk_On_Button'
            side_buttons[6].name = 'Solo_Button'
            side_buttons[7].name = 'Arm_Button'
            self._osd = M4LInterface()
            self._osd.name = "OSD"
            self._init_note_repeat()
            try:
                self._selector = MainSelectorComponent(matrix, tuple(top_buttons), tuple(side_buttons), self._config_button, self._osd, self, self._note_repeat, self._c_instance)
            except Exception as e:
                log("Could not create MainSelectorComponent: \n" + str(e))
                log(traceback.format_exc())
                raise e
            self._selector.name = 'Main_Modes'
            self._do_combine()
            for control in self.controls:
                if isinstance(control, ConfigurableButtonElement):
                    control.add_value_listener(self._button_value)
            
            self._suppress_session_highlight = False
            self.set_highlighting_session_component(self._selector.session_component())
            # due to our 2 stage init, we need to rebuild midi map 
            self.request_rebuild_midi_map()
            # and request update 
            self._selector.update()

            self.log_message("LaunchPad95 (mk2) Loaded !")

    def disconnect(self):
            self._suppress_send_midi = True
            for control in self.controls:
                if isinstance(control, ConfigurableButtonElement):
                    control.remove_value_listener(self._button_value)
            self._do_uncombine()
            if self._selector is not None:
                self._user_byte_write_button.remove_value_listener(self._user_byte_value)
                self._config_button.remove_value_listener(self._config_value)
            ControlSurface.disconnect(self)
            self._suppress_send_midi = False

            # launchpad mk2 needs disconnect string sent
            self._send_midi((240, 0, 32, 41, 2, 24, 64, 247))

            if self._config_button is not None:
                self._config_button.send_value(32)#Send enable flashing led config message to LP
                self._config_button.send_value(0)
                self._config_button = None
            if self._user_byte_write_button is not None:
                self._user_byte_write_button.send_value(0)
                self._user_byte_write_button = None

    def handle_sysex(self, midi_bytes):
            if len(midi_bytes) == 10 and midi_bytes[:7] == (240, 0, 32, 41, 2, 24, 64):
                response = int(midi_bytes[7])
                response += int(midi_bytes[8]) << 8
                if response == Live.Application.encrypt_challenge2(self._challenge):
                    self.log_message("Challenge Response ok (mk2)")
                    self._suppress_send_midi = False
                    self.set_enabled(True)

    def _send_challenge(self):
            # mk2
            challenge_bytes = tuple([ self._challenge >> 8 * index & 127 for index in range(4) ])
            self._send_midi((240, 0, 32, 41, 2, 24, 64) + challenge_bytes + (247,))
