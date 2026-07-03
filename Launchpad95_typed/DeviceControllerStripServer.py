from __future__ import annotations
from typing import Any, Optional, Tuple

import threading
import traceback

from .ButtonSliderElement import ButtonSliderElement
from .Settings import Settings
import time
from .Log import log

SLIDER_MODE_OFF = 0
SLIDER_MODE_TOGGLE = 1
SLIDER_MODE_SLIDER = 2
SLIDER_MODE_PRECISION_SLIDER = 3
SLIDER_MODE_SMALL_ENUM = 4
SLIDER_MODE_BIG_ENUM = 5
ROUNDTRIP_TARGET: float = 0.05

non_returns: list = [
    "set_precision_mode",
    "set_stepless_mode",
    "shutdown",
    "update",
    "reset_if_no_parameter",
    "_button_value",
    "connect_to",
    "release_parameter",
    "set_parent",
]

returning: list = ["set_enabled", "param_name", "param_value", "__ne__"]


class DeviceControllerStripServer(ButtonSliderElement, threading.Thread):
    def __init__(
        self,
        buttons: tuple,
        control_surface: Any,
        column: Any,
        request_queue: Any,
        response_queue: Any,
        parent: Any = None,
    ) -> None:
        ButtonSliderElement.__init__(self, buttons)
        self._buttons: Optional[Tuple[Any, ...]] = buttons
        self._control_surface = control_surface
        self._column = column
        self._request_queue = request_queue
        self._response_queue = response_queue
        self._parent = parent
        self._num_buttons: int = len(buttons)
        self._value_map: Tuple[float, ...] = tuple(
            [
                float(index) / (self._num_buttons - 1)
                for index in range(self._num_buttons)
            ]
        )
        self._last_value_map_index: int = -1
        self._precision_mode: bool = False
        self._stepless_mode: bool = False
        self._enabled: bool = True
        self._update_primed: bool = False
        self._parameter_stack: dict = {}
        self._current_value: Optional[float] = None
        self._last_value: Optional[float] = None
        self._last_sent_value: int = -1
        self._target_value: Optional[float] = None
        self._current_velocity: float = 10.0
        self.roundtrip_target: float = ROUNDTRIP_TARGET
        self.roundtrip_start: float = 0
        self.roundtrip_end: float = 0
        self.roundtrip_time: float = 0
        self.current_token: int = 0

        self._timed_mode: bool = Settings.ENABLE_TDC
        self._timed_start: float = 0
        self._timed_step: int = 0
        self._timed_step_size: float = Settings.TDC_MAX_TIME / len(Settings.TDC_MAP)
        self._last_pressed_index: int = -1
        self._primed_target_value: Optional[float] = None

    def set_enabled(self, enabled: bool) -> bool:
        self._enabled = enabled
        return self._enabled

    def set_parent(self, parent: Any) -> None:
        self._parent = parent

    def set_precision_mode(self, precision_mode: bool) -> None:
        self._precision_mode = precision_mode
        self.update()

    def set_stepless_mode(self, stepless_mode: bool) -> None:
        self._stepless_mode = stepless_mode
        self.update()

    def shutdown(self) -> None:
        self._control_surface = None
        self._parent = None
        self._column = None
        self._buttons = None

    @property
    def _value(self) -> float:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.value
        else:
            return 0

    def param_name(self) -> str:
        try:
            if self._parameter_to_map_to is not None:
                return self._parameter_to_map_to.name
            else:
                return "None"

        except Exception:
            return "None"

    def param_value(self) -> float:
        try:
            if self._parameter_to_map_to is not None:
                return self._parameter_to_map_to.value
            else:
                return 0
        except Exception:
            return 0

    @property
    def _max(self) -> float:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.max
        else:
            return 0

    @property
    def _min(self) -> float:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.min
        else:
            return 0

    @property
    def _range(self) -> float:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.max - self._parameter_to_map_to.min
        else:
            return 0

    @property
    def _default_value(self) -> Any:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to._default_value
        else:
            return 0

    @property
    def _is_quantized(self) -> bool:
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.is_quantized
        else:
            return False

    @property
    def _mode(self) -> int:
        if self._parameter_to_map_to is not None:
            if self._is_quantized:
                if self._range == 1:
                    return SLIDER_MODE_TOGGLE
                elif self._range <= self._num_buttons:
                    return SLIDER_MODE_SMALL_ENUM
                else:
                    return SLIDER_MODE_BIG_ENUM
            else:
                if self._precision_mode:
                    return SLIDER_MODE_PRECISION_SLIDER
                else:
                    return SLIDER_MODE_SLIDER
        else:
            return SLIDER_MODE_OFF

    def update(self) -> None:
        if self._enabled:
            if self._mode == SLIDER_MODE_TOGGLE:
                self._update_toggle()
            elif self._mode == SLIDER_MODE_SMALL_ENUM:
                self._update_small_enum()
            elif self._mode == SLIDER_MODE_BIG_ENUM:
                self._update_big_enum()
            elif self._mode == SLIDER_MODE_SLIDER:
                self._update_slider()
            elif self._mode == SLIDER_MODE_PRECISION_SLIDER:
                self._update_precision_slider()
            else:
                self._update_off()

    def reset(self) -> None:
        self._update_off()

    def reset_if_no_parameter(self) -> None:
        if self._parameter_to_map_to is None:
            self.reset()
        else:
            self._update_primed = True

    def _update_off(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        self._update_buttons(tuple(v))

    def _update_toggle(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value == self._max:
            v[0] = "Device.Toggle.On"
        else:
            v[0] = "Device.Toggle.Off"
        self._update_buttons(tuple(v))

    def _update_small_enum(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        for index in range(int(self._range + 1)):
            if self._value == index + self._min:
                v[index] = "Device.Enum.On"
            else:
                v[index] = "Device.Enum.Off"
        self._update_buttons(tuple(v))

    def _update_big_enum(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value > self._min:
            v[3] = "Device.BigEnum.On"
        else:
            v[3] = "Device.BigEnum.Off"
        if self._value < self._max:
            v[4] = "Device.BigEnum.On"
        else:
            v[4] = "Device.BigEnum.Off"
        self._update_buttons(tuple(v))

    def _update_slider(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        update_index: int = 0
        length: int = len(self._buttons)

        for index in range(length):
            current_value: float = self._value_map[index]
            prev_value: float = self._value_map[max(0, index - 1)]
            offset_third: float = (current_value - prev_value) / 3
            current_window: float = current_value * self._range + self._min
            one_third_window: float = (
                prev_value + offset_third
            ) * self._range + self._min
            second_third_window: float = (
                prev_value + offset_third * 2
            ) * self._range + self._min

            if self._value >= current_window:
                update_index = index
                if Settings.USE_CUSTOM_DEVICE_CONTROL_COLORS:
                    v[index] = "Device.CustomSlider" + str(self._column) + ".On"
                else:
                    v[index] = "Device.DefaultSlider.On"
            else:
                if Settings.USE_CUSTOM_DEVICE_CONTROL_COLORS:
                    if one_third_window <= self._value < second_third_window:
                        update_index = index
                        v[index] = "Device.CustomSlider" + str(self._column) + ".Third"
                    elif second_third_window <= self._value < current_window:
                        update_index = index
                        v[index] = "Device.CustomSlider" + str(self._column) + ".Half"
                    else:
                        v[index] = "Device.CustomSlider" + str(self._column) + ".Off"
                else:
                    v[index] = "Device.DefaultSlider.Off"
            if self._timed_mode and self._timed_start > 0 and self._stepless_mode:
                if index == self._last_pressed_index:
                    v[index] = "Device.ColorSteps.Step" + str(self._timed_step)

        self._last_value_map_index = update_index
        self._update_buttons(tuple(v))

    def _update_precision_slider(self) -> None:
        if self._buttons is None:
            return
        v: list = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value > self._min:
            v[3] = "Device.PrecisionSlider.On"
        else:
            v[3] = "Device.PrecisionSlider.Off"

        if self._value < self._max:
            v[4] = "Device.PrecisionSlider.On"
        else:
            v[4] = "Device.PrecisionSlider.Off"
        self._update_buttons(tuple(v))

    def _update_buttons(self, buttons: tuple) -> None:
        if self._buttons is None:
            return
        assert isinstance(buttons, tuple)
        assert len(buttons) == len(self._buttons)
        for index in range(len(self._buttons)):
            self._buttons[index].set_on_off_values(buttons[index], buttons[index])
            if buttons[index].endswith("On"):  # buttons[index]>0:
                self._buttons[index].turn_on()
            else:
                self._buttons[index].turn_off()

    def _button_value(self, value: int, sender: Any) -> None:
        if self._buttons is None:
            return
        assert isinstance(value, int)
        assert sender in self._buttons
        # log(f"button_value: value: {value} Mode: {self._mode} Range: {self._range} Momentary: {sender.is_momentary()}")
        self._last_sent_value = -1
        if self._parameter_to_map_to is not None and self._enabled:
            index_of_sender: int = list(self._buttons).index(sender)

            if (value != 0) or (not sender.is_momentary()):
                if value != self._last_sent_value:
                    target_value: float = self._parameter_to_map_to.value

                    if self._mode == SLIDER_MODE_TOGGLE and index_of_sender == 0:
                        if self._value == self._max:
                            target_value = self._min
                        else:
                            target_value = self._max

                    elif self._mode == SLIDER_MODE_SMALL_ENUM:
                        target_value = index_of_sender + self._min

                    elif self._mode == SLIDER_MODE_BIG_ENUM:
                        if index_of_sender >= 4:
                            inc = 2 ** (index_of_sender - 3 - 1)
                            if self._value + inc <= self._max:
                                target_value += inc
                            else:
                                target_value = self._max
                        else:
                            inc = 2 ** (4 - index_of_sender - 1)
                            if self._value - inc >= self._min:
                                target_value -= inc
                            else:
                                target_value = self._min

                    elif self._mode == SLIDER_MODE_SLIDER:
                        target_value = (
                            self._value_map[index_of_sender] * self._range + self._min
                        )

                    elif self._mode == SLIDER_MODE_PRECISION_SLIDER:
                        inc = float(self._range) / 128
                        if self._range > 7 and inc < 1:
                            inc = 1
                        if index_of_sender >= 4:
                            inc = inc * 2 ** (index_of_sender - 3 - 1)
                            if self._value + inc <= self._max:
                                target_value += inc
                            else:
                                target_value = self._max
                        else:
                            inc = inc * 2 ** (4 - index_of_sender - 1)
                            if self._value - inc >= self._min:
                                target_value -= inc
                            else:
                                target_value = self._min
                    if not self._timed_mode:
                        self.update_current_parameter_value(target_value, value)
                    else:
                        self._primed_target_value = target_value
                        self._timed_step = 0
                        self._timed_start = time.time()
                        self._last_pressed_index = index_of_sender

                    self.update()
                    if self._parent is not None:
                        self._custom_update_OSD()
            elif value == 0:
                index_of_sender = list(self._buttons).index(sender)
                if self._timed_mode and index_of_sender == self._last_pressed_index:
                    pressed_time: float = time.time() - self._timed_start
                    new_velocity: float = self._calc_velocity(pressed_time)

                    # log(f"Pressed time: {pressed_time} Index: {index_of_sender} Velo: {new_velocity}")
                    self.update_current_parameter_value(
                        self._primed_target_value, new_velocity
                    )

                    self._timed_start = 0
                    self._last_pressed_index = -1
                    self._primed_target_value = None
                    self._timed_step = 0
                    self.update()
                    if self._parent is not None:
                        self._custom_update_OSD()

    def _calc_velocity(self, pressed_time: float) -> float:
        factor: float = min(1.0, pressed_time / Settings.TDC_MAX_TIME)
        tdc_map_index: float = (len(Settings.TDC_MAP) - 1) * factor
        tdc_entry: float = Settings.TDC_MAP[int(tdc_map_index)]
        needed_rounds: float = tdc_entry / self.roundtrip_target
        needed_rounds = max(1.0, needed_rounds)
        change_per_round: float = self._range / needed_rounds
        velocity: float = change_per_round * 127.0
        # log(f"Step {self._timed_step} TDC Map Index: {int(tdc_map_index)} TDC Entry: {tdc_entry} Needed Rounds: {needed_rounds} Change per round: {change_per_round} Velocity: {velocity}")
        return velocity

    def update_current_parameter_value(
        self,
        new_target_value: Optional[float] = None,
        new_velocity: Optional[float] = None,
    ) -> None:
        target_value: float = (
            new_target_value
            if new_target_value is not None
            else (self._target_value if self._target_value is not None else 0.0)
        )
        velocity: float = (
            self._current_velocity if new_velocity is None else new_velocity
        )
        current_value: Optional[float] = self._current_value
        if current_value is None:
            return
        if (
            self._precision_mode
            or not self._stepless_mode
            or not self._mode == SLIDER_MODE_SLIDER
        ):
            tries: int = 0
            while True:
                try:
                    self._parameter_to_map_to.value = target_value
                    break
                except RuntimeError:
                    tries += 1
                    if tries % 100 == 0:
                        # log(f"A Current-{self._column}: RuntimeError for parameter {self._parameter_to_map_to.name}")
                        pass
                    if tries > 500:
                        log(
                            " Current-"
                            + str(self._column)
                            + ": RuntimeError for parameter "
                            + self._parameter_to_map_to.name
                            + " !!!"
                        )
                        break
                    continue
            self._current_value = self._parameter_to_map_to.value
            self._target_value = self._current_value
            self._last_value = self._current_value
        else:
            if self._target_value != target_value or self._current_velocity != velocity:
                self._target_value = target_value
                self._current_velocity = velocity
            if target_value != current_value:
                max_diff: float = abs(target_value - current_value)
                value_offset: float = self.calc_value_offset(velocity, max_diff)
                new_value: float = (
                    current_value + value_offset
                    if current_value < target_value
                    else current_value - value_offset
                )
                new_value = max(
                    min(new_value, self._parameter_to_map_to.max),
                    self._parameter_to_map_to.min,
                )
                tries = 0
                failed: bool = False
                while True:
                    try:
                        self._parameter_to_map_to.value = new_value
                        break
                    except RuntimeError:
                        tries += 1
                        if tries % 100 == 0:
                            # log(f"C Current-{self._column}: RuntimeError for parameter {self._parameter_to_map_to.name}")
                            pass
                        if tries > 1000:
                            # log(f"D Current-{self._column}: RuntimeError for parameter {self._parameter_to_map_to.name} !!!")
                            failed = True
                            break
                        continue
                self._current_value = self._parameter_to_map_to.value
                self._last_value = self._current_value
                if not failed and self._is_update_needed():
                    self.update()

    def update_parameter_stack(self) -> None:
        to_remove: list = []
        for param_id, param in self._parameter_stack.items():
            try:
                parameter = param["parameter"]
                param["current_value"] = parameter.value
                if param["current_value"] != param["target_value"]:
                    if round(param["last_value"], 5) == round(
                        param["current_value"], 5
                    ):
                        target_value: float = param["target_value"]
                        velocity: int = param["current_velocity"]
                        current_value: float = param["current_value"]
                        max_diff: float = abs(target_value - current_value)
                        value_offset: float = self.calc_value_offset(velocity, max_diff)
                        new_value: float = (
                            current_value + value_offset
                            if current_value < target_value
                            else current_value - value_offset
                        )
                        new_value = max(min(new_value, parameter.max), parameter.min)
                        tries = 0
                        while True:
                            try:
                                parameter.value = new_value
                                param["current_value"] = new_value
                                param["last_value"] = new_value
                                break
                            except RuntimeError:
                                tries += 1
                                if tries % 100 == 0:
                                    # log(f"A Stacks-{self._column}: RuntimeError for parameter {parameter.name} ({tries})")
                                    pass
                                if tries > 500:
                                    # log(f"B Stacks-{self._column}: RuntimeError for parameter {parameter.name}:\n {e} !!!")
                                    break
                                continue
                        if new_value == param["target_value"]:
                            to_remove.append(param_id)
                    else:
                        to_remove.append(param_id)
                else:
                    log(
                        "Parameter "
                        + parameter.name
                        + " is already at target value !!!!!!!!!!!!!!"
                    )
                    to_remove.append(param_id)
            except Exception as e:
                if "Python argument types in" in str(e):
                    to_remove.append(param_id)
                    continue
                raise e
        for param_id in to_remove:
            del self._parameter_stack[param_id]

    def run(self) -> None:
        try:
            while True:
                if not self._request_queue.empty():
                    item: tuple = self._request_queue.get()
                    funct_name = item[0]
                    token = item[1]
                    args = item[2]
                    kwargs = item[3]
                    if funct_name == "shutdown":
                        # log(f"Shutting down DCSServer {self._column}")
                        return
                    else:
                        self._request_handler(funct_name, token, *args, **kwargs)
                roundtrip_time: float = time.time() - self.roundtrip_start
                time.sleep(max(0.0, self.roundtrip_target / 10 - roundtrip_time))
                if (
                    self._request_queue.empty()
                    or roundtrip_time > self.roundtrip_target
                ):
                    self.roundtrip_end = time.time()
                    self.roundtrip_time = self.roundtrip_end - self.roundtrip_start
                    self.roundtrip_start = self.roundtrip_end
                    if self._timed_mode and self._timed_start > 0:
                        self._timed_step = min(
                            9,
                            (
                                int(
                                    (self.roundtrip_end - self._timed_start)
                                    // self._timed_step_size
                                )
                            ),
                        )

                        self.update()
                        if self._parent is not None:
                            self._custom_update_OSD()

                    if self._parameter_to_map_to is not None:
                        # if (self._parameter_to_map_to != None and self._enabled):
                        try:
                            self._current_value = self._parameter_to_map_to.value
                        except Exception:
                            continue

                        if self._target_value is None or self._last_value is None:
                            self._target_value = self._current_value
                            self._last_value = self._current_value

                        if self._current_value != self._target_value:
                            if round(self._last_value, 5) == round(
                                self._current_value, 5
                            ):
                                self.update_current_parameter_value()
                            else:
                                # log(f"Parameter {self._parameter_to_map_to.name} changed while moving, Dropping!!")
                                self._last_value = self._current_value
                                self._target_value = self._current_value
                    self.update_parameter_stack()

        except Exception as e:
            log(
                "Run-Loop Exception in DCSServer "
                + str(self._column)
                + ": Type "
                + type(e).__name__
                + "\n "
                + str(e)
            )
            log(traceback.format_stack())
            log(traceback.format_exc())
            self._response_queue.put((0, "ERROR"))
            raise e

    def _request_handler(
        self, funct_name: str, token: int, *args: Any, **kwargs: Any
    ) -> None:
        # log(f"DCSServer {self._column} Request handler: {funct_name} with {args} and {kwargs}")
        self.current_token = token
        result: Optional[Any] = None
        if funct_name == "release_parameter":
            self.releasing_parameter(funct_name, *args, **kwargs)  # result = "None"
        elif funct_name == "connect_to":
            self.connecting_to(funct_name, *args, **kwargs)  # result = "None"
        elif funct_name in non_returns:
            # log(f"DCSServer {self._column} _request_handler: non return function {funct_name} with {args} and {kwargs}")
            self._call_dispatcher(funct_name, *args, **kwargs)
        elif funct_name in returning:
            # log(f"DCSServer {self._column} _request_handler: return function {funct_name} with {args} and {kwargs}")
            result = self._call_dispatcher(funct_name, *args, **kwargs)
        elif False:
            pass
        else:
            log(
                "DCSServer "
                + str(self._column)
                + " _request_handler: unknown function "
                + str(funct_name)
            )
            result = self._call_dispatcher(funct_name, *args, **kwargs)

        # log(f"DCSServer {self._column} Call dispatcher: {funct_name} returned {type(result)}")
        if result is not None:
            self._response_queue.put((token, result))

    def releasing_parameter(self, funct_name: str, *args: Any, **kwargs: Any) -> None:
        if self._parameter_to_map_to is not None and self._target_value is not None:
            try:
                if not self._parameter_to_map_to.value == self._target_value:
                    # log(f"A {self._column} Putting {self._parameter_to_map_to.name} on stack")
                    self._put_parameter_on_stack()
            except Exception:
                self._enabled = False
                # this is the case when a device gets deleted and the connection is made to the previous in chain device
                pass
        self._parameter_to_map_to = None
        self._call_dispatcher(funct_name, *args, **kwargs)

    def connecting_to(self, funct_name: str, *args: Any, **kwargs: Any) -> None:
        if self._parameter_to_map_to is not None:
            try:
                if not self._parameter_to_map_to.value == self._target_value:
                    # log(f"B {self._column} Putting {self._parameter_to_map_to.name} on stack")
                    self._put_parameter_on_stack()
            except Exception:
                # this is the case when a device gets deleted and the connection is made to the previous in chain device
                pass
            self._call_dispatcher(funct_name, *args, **kwargs)
            param_id = self._parameter_to_map_to._live_ptr
            if param_id in self._parameter_stack.keys():
                param = self._parameter_stack[param_id]
                value = self._parameter_to_map_to.value
                self._current_value = value
                self._last_value = value
                self._target_value = param["target_value"]
                self._current_velocity = param["current_velocity"]
                # log(f"Stacks-{self._column}: Parameter {param['parameter'].name} restored from stack {self._current_value} {self._target_value} {self._last_value} {self._current_velocity}")
                del self._parameter_stack[param_id]
            else:
                value = self._parameter_to_map_to.value
                self._current_value = value
                self._last_value = value
                self._target_value = value
                self._current_velocity = 10
        else:
            self._call_dispatcher(funct_name, *args, **kwargs)
            if self._parameter_to_map_to is not None:
                value = self._parameter_to_map_to.value
                self._current_value = value
                self._last_value = value
                self._target_value = value
                self._current_velocity = 10

    def _put_parameter_on_stack(self) -> None:
        value = self._parameter_to_map_to.value
        if self._parameter_to_map_to._live_ptr not in self._parameter_stack.keys():
            self._parameter_stack[self._parameter_to_map_to._live_ptr] = {
                "parameter": self._parameter_to_map_to,
                "current_value": value,
                "last_value": value,
                "target_value": self._target_value,
                "current_velocity": self._current_velocity,
            }

    def _call_dispatcher(
        self, method_name: str, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        # log(f"DCSServer {self._column} calling {method_name} with {args} and {kwargs}")
        try:
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    return method(*args, **kwargs)
                else:
                    log(
                        "DCSServer "
                        + str(self._column)
                        + "method "
                        + method_name
                        + " is not callable"
                    )
            else:
                log("DCSServer " + str(self._column) + " has no method " + method_name)
            return None
        except Exception as e:
            log(
                "Exception in DCSServer "
                + str(self._column)
                + " _call_dispatcher :\n "
                + str(e)
            )
            traceback.print_exc()
            log(traceback.format_stack())
            raise e

    # when called from connect_to, trigger_osd should be false
    def _on_parameter_changed(self, trigger_osd: bool = True) -> None:
        # log(traceback.format_stack())
        # log(f"DCSServer {self._column} _on_parameter_changed {trigger_osd}")
        if self._enabled:
            assert self._parameter_to_map_to is not None
            if self._is_update_needed():
                self.update()
            if self._parent is not None:
                # this might be called be background thread -> crash
                #
                self._custom_update_OSD(trigger_osd)  # self._custom_update_OSD(False)

    def _custom_update_OSD(self, trigger_osd: bool = True) -> None:
        if self._parent._osd is not None:
            self._parent._osd.mode = "Device Controller"
            name = self.param_name()
            if name != "None":
                self._parent._osd.attribute_names[self._column] = str(name)
                self._parent._osd.attributes[self._column] = str(self.param_value())
            else:
                self._parent._osd.attribute_names[self._column] = " "
                self._parent._osd.attributes[self._column] = " "
            # this might be called be background thread -> crash
            if trigger_osd:
                self._parent._osd.update()

    def calc_value_offset(self, velocity: float, max_diff: float) -> float:
        # log(f"Velocity: {velocity} Max diff: {max_diff}")
        if not self._timed_mode:
            if velocity > Settings.VELOCITY_THRESHOLD_MAX:
                return max_diff
            velocity = max(velocity, Settings.VELOCITY_THRESHOLD_MIN) ** 3
            velocity_factor: float = velocity / (Settings.VELOCITY_FACTOR * 127.0)
            change_per_roundtrip: float = velocity_factor / self.roundtrip_target
            value_offset: float = change_per_roundtrip * self.roundtrip_time
        else:
            velocity_factor = velocity / 127.0
            change_per_roundtrip = velocity_factor / self.roundtrip_target
            value_offset = change_per_roundtrip * self.roundtrip_time
        return min(value_offset, max_diff)

    def _is_update_needed(self) -> bool:
        if self._update_primed:
            self._update_primed = False
            return True
        if self._last_value_map_index == -1:
            return True
        if (self._value // self._value_map[1]) != self._last_value_map_index:
            return True
        return False

    def __ne__(self, other: Any) -> bool:
        return not self == other
