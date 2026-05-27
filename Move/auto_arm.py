# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: auto_arm.pyc (Python 3.11)

from ableton.v3.control_surface.components import AutoArmComponent as AutoArmComponentBase
from ableton.v3.control_surface.components.auto_arm import track_can_be_auto_armed

class AutoArmComponent(AutoArmComponentBase):
    
    def restore_auto_arm(self):
        if self.application.number_of_push_apps_running == 0 or self.needs_restore_auto_arm:
            song = self.song
            exclusive_arm = song.exclusive_arm
            for track in song.tracks:
                if (exclusive_arm or track_can_be_auto_armed(track)) and track.can_be_armed:
                    track.arm = False
                return None
                return None
                return None
