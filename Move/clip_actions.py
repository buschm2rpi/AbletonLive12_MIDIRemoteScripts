# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: clip_actions.pyc (Python 3.11)

from ableton.v3.control_surface.components import ClipActionsComponent as ClipActionsComponentBase
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.live import action
from suppressible_action_button import is_immediate_release_action_suppressed

class ClipActionsComponent(ClipActionsComponentBase):
    delete_button = ButtonControl(color = None)
    duplicate_button = ButtonControl(color = None)
    delete_button = (lambda self, _: if not is_immediate_release_action_suppressed(self.delete_button):
clip = self._target_track.target_clipif action.delete(clip):
self.notify(self.notifications.Clip.delete, 'Clip')NoneNone.notify(self.notifications.Clip.error_delete_empty_slot)None)()
    duplicate_button = (lambda self, _: if not self.any_clipboard_has_content or is_immediate_release_action_suppressed(self.duplicate_button):
clip = self._target_track.target_clipif action.duplicate_clip_special(clip):
self.notify(self.notifications.Clip.duplicate, 'Clip')NoneNoneNone)()
    
    def _update_delete_button(self):
        pass

    
    def _update_duplicate_button(self):
        pass
