# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: mixer.pyc (Python 3.11)

from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.components import SendIndexControlComponent as SendIndexControlComponentBase

class SendIndexControlComponent(SendIndexControlComponentBase):
    
    def _get_send_range_string(self):
        send_index = self.send_index
        num_sends = self.num_sends
        first_send_name = self._song.return_tracks[send_index].name
        if send_index == num_sends - 1:
            return '{}\n-'.format(first_send_name)
        return None.format(first_send_name, self._song.return_tracks[send_index + 1].name)

    
    def _notify_send_range(self, _):
        self.notify(self.notifications.generic, 'Sends\n{}'.format(self._get_send_range_string()))



class MixerComponent(MixerComponentBase):
    pass
# WARNING: Decompyle incomplete

