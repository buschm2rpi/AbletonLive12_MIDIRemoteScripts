from __future__ import annotations

from typing import Tuple


class Settings:
    # Add Stop buttons at the bottom of the Session. Experimental
    # SESSION__STOP_BUTTONS = True
    SESSION__STOP_BUTTONS: bool = False

    # Link sessions between multiple launchpad95. Experimental
    # SESSION__LINK = True
    SESSION__LINK: bool = False

    # Link stepseq to follow session. Experimental
    # STEPSEQ__LINK_WITH_SESSION = True
    STEPSEQ__LINK_WITH_SESSION: bool = False

    # Should the step sequencer scroll automatically to the currently playing page
    STEPSEQ__AUTO_SCROLL: bool = False

    # configure what user modes buttons do.
    # the 3 first value configure the 3 sub modes of button user mode 1,
    # and following ones are for user mode 2 button
    USER_MODES_1: list[str] = [
        "instrument",
        "device",
        # ,"user 1"
    ]
    USER_MODES_2: list[str] = [
        "drum stepseq",
        "melodic stepseq",
        # ,"user 2"
    ]

    # Device control mode
    DEVICE_CONTROLLER__STEPLESS_MODE: bool = True
    # device control stepless fader velocity thresholds
    # if velocity is above threshold, the parameter will be changed instantly
    VELOCITY_THRESHOLD_MAX: int = 100
    VELOCITY_THRESHOLD_MIN: int = 40
    # used for the gradient of the parameter change
    # the higher the value, the slower the parameter change
    VELOCITY_FACTOR: float = (127**2) * (127 / 2)
    USE_CUSTOM_DEVICE_CONTROL_COLORS: bool = False
    # time sensitive stepless fader
    ENABLE_TDC: bool = True
    # Time you have to keep the button pressed for the slowest velocity
    TDC_MAX_TIME: float = 2.0
    # The number of seconds it takes for a parameter to change from min to max value for each step
    TDC_MAP: list[float] = [0, 0.75, 1.5, 3, 5, 8, 12, 17, 25, 40]

    # Logging feature for debugging (creates C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt)
    LOGGING: bool = False

    # Map buttons to levels in volume slider. Exactly 7 values must be provided.
    # The lowest button is always set to -inf. Lowest supported value is -69 dB.
    # So far the values are not exact: -24 dB below equals -23.7 dB in Ableton.
    VOLUME_LEVELS: Tuple[int, ...] = (6, 0, -6, -12, -18, -24, -42)
