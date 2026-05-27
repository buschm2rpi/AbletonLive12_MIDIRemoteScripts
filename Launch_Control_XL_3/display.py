# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: display.pyc (Python 3.11)

from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from typing import Optional, Tuple
from ableton.v3.base import flatten
from ableton.v3.control_surface.display import DefaultNotifications, DisplaySpecification, Text, view
from ableton.v3.live import display_name, find_parent_track, liveobj_name, liveobj_valid
DisplayText = partial(Text, max_width = 16, justification = Text.Justification.NONE)

class ControlType(IntEnum):
    faders = 0
    upper_encoders = 1
    lower_encoders = 2


class Config(IntEnum):
    two_line = 97
    three_line = 98

TargetContent = <NODE:12>()
DisplayContent = <NODE:12>()

class Notifications(DefaultNotifications):
    generic = DefaultNotifications.DefaultText()
    identify = DefaultNotifications.TransformDefaultText((lambda x: '\n{}'.format(x.replace('Connected', ''))))
    
    class Device(DefaultNotifications.Device):
        bank = DefaultNotifications.DefaultText()

    
    class Modes(DefaultNotifications.Modes):
        
        select = lambda _, mode_name: 'mode:{}'.format(mode_name)



def render_mode_notification(mode):
    if mode in ('solo', 'arm', 'mute', 'track_select'):
        return DisplayContent(temp = TargetContent(lines = ('Button Function', mode.replace('_', ' ').title())))


def render_notification(_, notification_text):
    if notification_text.startswith('mode:'):
        return render_mode_notification(notification_text.replace('mode:', ''))
    if None in notification_text:
        lines = tuple(notification_text.split('\n'))
        return DisplayContent(temp = TargetContent(config = Config.three_line if len(lines) == 3 else Config.two_line, lines = lines))


def create_root_view():
    main_view = (lambda state = None: pass# WARNING: Decompyle incomplete
)()
    return view.CompoundView(view.DisconnectedView(), view.NotificationView(render_notification, duration = 0.1, supports_new_line = True), main_view)


def protocol(elements):
    pass
# WARNING: Decompyle incomplete

display_specification = DisplaySpecification(create_root_view = create_root_view, protocol = protocol, notifications = Notifications)
