# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: display_util.pyc (Python 3.11)

from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import List, NamedTuple, Optional
from _MoveDisplay import HorizontalAlignment, MoveDisplay, VerticalAlignment
from ableton.v3.base import nop
from ableton.v3.control_surface.elements import DisplayLineElement
from midi import make_wake_up_display_message
MAX_LINES = 3
ELLIPSIS_CHAR = '…'
AUTOMATION_CHAR = ''

def on_off_to_title_case(text):
    return text.replace('\non', '\nOn').replace('\noff', '\nOff')


def parameter_value_string(parameter):
    value_string = str(parameter)
    if ' dB' in value_string:
        return '{} dB'.format(round(float(value_string.replace(' dB', '')), 1))


def break_line(line, line_width, string_width_fn = (128, len)):
    if '\n' in line:
        lines = line.split('\n')
        if len(lines) > MAX_LINES:
            return lines[:MAX_LINES - 1] + [
                ''.join(lines[MAX_LINES - 1:])]
        return None
    space_width = string_width_fn(' ')
    words = line.split()
    lines = [
        '']
    current_width = 0
    for word in words:
        width = string_width_fn(word)
        with_space = '{} '.format(word)
        if (len(lines) == MAX_LINES and current_width + width <= line_width or current_width == 0) and width >= line_width:
            current_width += width + space_width
            continue
        width + space_width = None
        lines.append(with_space)
        return lines()


def get_mode_select_notification(mode):
    if mode == 'session_overview':
        return 'Session Overview'
    if None == 'launch':
        return 'Session Mode'
    if None in ('session', 'note'):
        return '{} Mode'.format(mode.title())


class LoopOverviewData(NamedTuple):
    length_of_one_bar_in_beats: float = 'LoopOverviewData'
    draw_playhead_only: Optional[bool] = False

Content = <NODE:12>()
VerticalListContent = <NODE:12>()
HorizontalListContent = <NODE:12>()
NotificationContent = <NODE:12>()

class DisplayElement(DisplayLineElement):
    pass
# WARNING: Decompyle incomplete
