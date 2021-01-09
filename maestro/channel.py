from __future__ import annotations

import functools
import typing

from maestro.constants import CONTROL_TRANSFER_SET_TYPE
from maestro.enums import ChannelMode, Request, ServoVariableMask, USCParameter

if typing.TYPE_CHECKING:
    from maestro import Maestro


def _require_channel_mode(*modes: typing.Iterable[ChannelMode]):
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(self: Channel, *args, **kwargs):
            if self.mode not in modes:
                raise ValueError(
                    f"Requires a channel mode of {', '.join(map(str, modes))}, not {self.mode}"
                )
            return f(self, *args, **kwargs)

        return wrapped

    return wrapper


def _servo_parameter(parameter: USCParameter, doc: str):
    @_require_channel_mode(ChannelMode.Servo)
    def getter(self):
        return self.maestro.get_raw_parameter(parameter + self.index * 9)

    getter.__doc__ = doc

    @_require_channel_mode(ChannelMode.Servo)
    def setter(self, value):
        self.maestro.set_raw_parameter(parameter + self.index * 9, value)

    return property(getter, setter)


class Channel:
    """A channel on a Maestro servo controller."""

    def __init__(self, maestro: Maestro, index: int, mode: ChannelMode):
        self.maestro = maestro
        self.index = index
        self._mode = mode

        self._position = None
        self._target = None
        self._speed = None
        self._acceleration = None

    def set_servo_variable(self, variable_mask: ServoVariableMask, value: int):
        self.maestro.dev.ctrl_transfer(
            CONTROL_TRANSFER_SET_TYPE,
            Request.SetServoVariable,
            wValue=value,
            wIndex=self.index | variable_mask,
        )

    def get_servo_parameter(self, parameter: USCParameter):
        return self.maestro.get_raw_parameter(parameter + self.index * 9)

    def set_servo_parameter(self, parameter: USCParameter, value: int):
        return self.maestro.set_raw_parameter(parameter + self.index * 9, value)

    @property
    def mode(self) -> ChannelMode:
        return self._mode

    @mode.setter
    def mode(self, mode: ChannelMode):
        self.maestro._set_mode(self.index, mode)
        self._mode = mode

    @property
    @_require_channel_mode(ChannelMode.Input)
    def value(self) -> float:
        """The value read by this input, in the range [0, 1)."""
        return self._target / (2 ** 10)

    @property
    @_require_channel_mode(ChannelMode.Servo)
    def position(self):
        """Where the servo controller believes this servo to be currently positioned.

        Note that this is where the servo is currently being told to be, which will
        not necessarily be the target if speed and/or acceleration are non-zero.

        :returns: The current position, in ms."""
        return self._position / 4

    @property
    @_require_channel_mode(ChannelMode.Servo)
    def speed(self):
        return self._speed

    @speed.setter
    @_require_channel_mode(ChannelMode.Servo)
    def speed(self, value):
        self.set_servo_variable(ServoVariableMask.Speed, value)

    @property
    @_require_channel_mode(ChannelMode.Servo, ChannelMode.Output)
    def target(self):
        """The current target position, in ms."""
        return self._target / 4

    @target.setter
    @_require_channel_mode(ChannelMode.Servo)
    def target(self, value: int):
        assert 1000 <= value <= 2000
        self.maestro.dev.ctrl_transfer(
            CONTROL_TRANSFER_SET_TYPE,
            Request.SetTarget,
            wValue=value * 4,
            wIndex=self.index,
        )

    @property
    @_require_channel_mode(ChannelMode.Servo)
    def acceleration(self):
        return self._acceleration

    min = _servo_parameter(USCParameter.ServoMinBase)
    max = _servo_parameter(USCParameter.ServoMaxBase)
    home = _servo_parameter(
        USCParameter.ServoHomeBase,
    )
    neutral = _servo_parameter(
        USCParameter.ServoNeutralBase,
        "This option specifies the target value, in microseconds, that corresponds to 127 (neutral) for 8-bit commands.",
    )
