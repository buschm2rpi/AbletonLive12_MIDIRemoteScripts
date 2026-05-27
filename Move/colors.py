# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: colors.pyc (Python 3.11)

from colorsys import hsv_to_rgb, rgb_to_hsv
from enum import IntEnum
from functools import partial
from ableton.v3.base import hex_to_rgb
from ableton.v3.control_surface.elements import ColorPart, ComplexColor, FallbackColor, SimpleColor
from ableton.v3.live import liveobj_valid
from step_button import ColorWithAnimatedIcon, ColorWithSimpleIcon
TRANSLATED_WHITE_INDEX = 7
WHITE_RGB_VALUE = 122
DARK_GREY_RGB_VALUE = 124
DARK_GREY_MONO_VALUE = 16
PULSE_BASE_CHANNEL = 6
BLINK_BASE_CHANNEL = 11

class AnimationSpeed(IntEnum):
    quarter = 3
    half = 4


def make_animated_color(primary_color, secondary_color, speed, base_channel = (AnimationSpeed.quarter, 0)):
    return ComplexColor((ColorPart(secondary_color.midi_value), ColorPart(primary_color.midi_value, channel = speed + base_channel)))

make_pulsing_color = partial(make_animated_color, base_channel = PULSE_BASE_CHANNEL)
make_blinking_color = partial(make_animated_color, base_channel = BLINK_BASE_CHANNEL)

def make_color_for_liveobj(obj):
    return SimpleColor(translate_color_index(obj))


def make_dimmed_color_for_liveobj(obj, shade_level = (2,)):
    return SimpleColor(determine_shaded_color_index(translate_color_index(obj), shade_level))


def make_pulsing_color_for_liveobj(obj):
    return make_pulsing_color(make_color_for_liveobj(obj), make_dimmed_color_for_liveobj(obj))


def translate_color_index(obj):
    if liveobj_valid(obj) and obj.color_index in range(len(COLOR_INDEX_TO_MOVE_INDEX)):
        return COLOR_INDEX_TO_MOVE_INDEX[obj.color_index]


def determine_shaded_color_index(color_index, shade_level):
    if color_index == WHITE_RGB_VALUE:
        return color_index + shade_level
    return (None - 1) * 2 + 64 + shade_level


def hex_to_hsv(hex_value):
    pass
# WARNING: Decompyle incomplete


def adjust_hsv_brightness(h, s, v, amount):
    return hsv_to_rgb(h, s, v * amount)()


def rgb_to_move(r, g, b):
    return (r & 127, r >> 7 & 1, g & 127, g >> 7 & 1, b & 127, b >> 7 & 1)


class Colors:
    OFF = SimpleColor(0)
    WHITE = SimpleColor(WHITE_RGB_VALUE)
    WHITE_PULSE_HALF = make_pulsing_color(WHITE, SimpleColor(DARK_GREY_MONO_VALUE), speed = AnimationSpeed.half)
    LIGHT_GREY = SimpleColor(123)
    DARK_GREY = FallbackColor(SimpleColor(DARK_GREY_RGB_VALUE), SimpleColor(DARK_GREY_MONO_VALUE))
    GREEN = SimpleColor(126)
    GREEN_BLINK_QUARTER = make_blinking_color(OFF, GREEN)
    RED = SimpleColor(127)
    RED_SHADE = SimpleColor(27)
    RED_BLINK_QUARTER = make_blinking_color(OFF, RED)
    BLUE = SimpleColor(125)
    WHITE_WITH_ICON = ColorWithSimpleIcon(WHITE_RGB_VALUE)
    WHITE_WITH_ICON_PULSE_HALF = ColorWithAnimatedIcon((ColorPart(DARK_GREY_MONO_VALUE), ColorPart(WHITE_RGB_VALUE, channel = AnimationSpeed.half + PULSE_BASE_CHANNEL)))
    DARK_GREY_WITH_ICON = ColorWithSimpleIcon(DARK_GREY_RGB_VALUE)

COLOR_INDEX_TO_MOVE_INDEX = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 7, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 5, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 22, 25, 17, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 21, 2, 4, 6, 8, 10, 12, 14, 20, 19, 18, 22, 23, 26, 6)
COLOR_TABLE = ((0, 0, 0), (1, 16728114, 2), (2, 8389632, 4), (3, 13188096, 6), (4, 11280128, 8), (5, 9195544, 10), (6, 4790276, 12), (7, 16440379, 14), (8, 16762134, 16), (9, 11992846, 18), (10, 7995160, 20), (11, 3457558, 22), (12, 5212676, 24), (13, 6487893, 26), (14, 2719059, 28), (15, 2530930, 30), (16, 3255807, 32), (17, 3564540, 34), (18, 1717503, 36), (19, 1838310, 38), (20, 1391001, 40), (21, 3749887, 42), (22, 5710591, 44), (23, 9907199, 46), (24, 8724856, 48), (25, 16715826, 50), (26, 16722900, 52), (27, 10892321, 54), (28, 10049064, 56), (29, 8873728, 58), (30, 9470495, 60), (31, 4884224, 62), (32, 32530, 64), (33, 1594290, 66), (34, 6441901, 68), (35, 7551591, 70), (36, 16301231, 72), (37, 16751478, 74), (38, 16760671, 76), (39, 14266225, 78), (40, 16774272, 80), (41, 12565097, 80), (42, 12373128, 81), (43, 11468697, 81), (44, 8183199, 82), (45, 9024637, 82), (46, 8451071, 83), (47, 8048380, 83), (48, 6857171, 84), (49, 8753090, 85), (50, 12298994, 85), (51, 13482980, 86), (52, 15698864, 86), (53, 8756620, 87), (54, 7042414, 87), (55, 8687771, 88), (56, 6975605, 88), (57, 8947101, 89), (58, 7105141, 90), (59, 10323356, 90), (60, 7629428, 91), (61, 10263941, 91), (62, 7632234, 92), (63, 10323076, 92), (64, 7694954, 93), (65, 6691092, 93), (66, 2164742, 94), (67, 4588288, 94), (68, 2621440, 95), (69, 6100736, 96), (70, 2100480, 96), (71, 4656128, 97), (72, 1837056, 97), (73, 3877652, 98), (74, 1839882, 98), (75, 2428421, 99), (76, 853506, 99), (77, 6576151, 100), (78, 2104327, 101), (79, 6704648, 101), (80, 2169090, 102), (81, 4744709, 102), (82, 1515777, 103), (83, 3171849, 103), (84, 991491, 104), (85, 1330440, 104), (86, 399618, 105), (87, 2045697, 106), (88, 659712, 106), (89, 2582050, 107), (90, 794891, 107), (91, 1326633, 108), (92, 530704, 108), (93, 19766, 109), (94, 6158, 109), (95, 1262950, 110), (96, 398881, 110), (97, 1386340, 111), (98, 461856, 112), (99, 660582, 112), (100, 198177, 113), (101, 722012, 113), (102, 196893, 114), (103, 662604, 114), (104, 264990, 115), (105, 1447526, 115), (106, 460577, 116), (107, 2231654, 117), (108, 721953, 117), (109, 3936614, 118), (110, 1246497, 118), (111, 3476784, 119), (112, 1115151, 119), (113, 6686228, 120), (114, 2163206, 120), (115, 6689108, 121), (116, 2163995, 122), (117, 0, 122), (118, 5855577, 123), (119, 1710618, 123), (120, 16777215, 124), (121, 5855577, 124), (122, 13421772, 125), (123, 4210752, 125), (124, 1315860, 126), (125, 255, 126), (126, 65280, 127), (127, 16711680, 127))
