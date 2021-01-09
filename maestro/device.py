from __future__ import annotations

import math
import typing
from typing import List

import usb.core

from .channel import Channel
from .constants import CONTROL_TRANSFER_REQUEST_TYPE, CONTROL_TRANSFER_SET_TYPE
from .enums import ChannelMode, Request, USCParameter, get_parameter_size
from .exceptions import NoMaestroAvailable
from .structs import ServoStatus

__all__ = ["Maestro"]


def is_maestro(dev):
    return dev.idVendor == 0x1FFB and dev.idProduct in (137, 138, 139, 140)


PRODUCT_CHANNEL_COUNTS = {
    137: 6,
    138: 12,
    139: 18,
    140: 24,
}


class Maestro:
    """A Maestro servo controller.

    You shouldn't instantiate this class directly. Instead you should use one of the
    following class methods:

    * :py:meth:`Maestro.get_all`
    * :py:meth:`Maestro.get_one`
    * :py:meth:`Maestro.get_by_serial_number`

    """

    _group_modes: List[int]

    def __init__(self, dev: usb.core.Device, timeout=5000):
        if type(self) == Maestro:
            raise TypeError("Don't initialize this directly; use Maestro.for_device()")

        self.dev = dev
        self.timeout = timeout

        modes = self._get_modes()

        self._channels = [
            Channel(self, i, mode=modes[i]) for i in range(self.channel_count)
        ]

    def __repr__(self):
        return f'<{self.__module__}.{self.__class__.__name__} "{self.serial_number}">'

    @property
    def channel_count(self) -> int:
        """The number of available channels on this servo controller."""
        return PRODUCT_CHANNEL_COUNTS[self.dev.idProduct]

    @classmethod
    def for_device(cls, dev: usb.core.Device, **kwargs) -> Maestro:
        """Returns a Maestro instance for the given pyusb Device."""
        if not is_maestro(dev):
            raise ValueError("This isn't a Maestro")
        if dev.idProduct == 137:
            return MicroMaestro(dev, **kwargs)
        else:
            return MiniMaestro(dev, **kwargs)

    def _get_group_modes(self):
        try:
            return self._group_modes
        except AttributeError:
            self._group_modes = [
                self.get_raw_parameter(USCParameter.ChannelModes0To3 + i)[0]
                for i in range(self.channel_count // 4)
            ]
            return self._group_modes

    def _get_modes(self) -> List[ChannelMode]:
        modes = []
        for group_mode in self._get_group_modes():
            for j in range(4):
                modes.append(ChannelMode(group_mode & 0b11))
                group_mode >>= 2
        return modes

    def _set_mode(self, index: int, mode: ChannelMode):
        group_modes = self._get_group_modes()
        i, j = index // 4, (index % 4) * 2
        value = mode << j
        mask = 0xFF ^ (0b11 << j)
        self._group_modes[i] = group_modes[i] & mask | value
        self.set_raw_parameter(USCParameter.ChannelModes0To3 + i, self._group_modes[i])

    def __getitem__(self, index) -> Channel:
        return self._channels[index]

    @property
    def serial_number(self) -> str:
        """The self-reported serial number for this device.

        You may use this later as an argument to :py:meth:`Maestro.get_by_serial_number`
        to ensure you connect to the same device again, in the case where multiple
        Maestro devices are connected."""
        return self.dev.serial_number

    def refresh_variables(self):
        raise NotImplementedError

    def get_raw_parameter(self, parameter: USCParameter) -> int:
        return self.dev.ctrl_transfer(
            CONTROL_TRANSFER_REQUEST_TYPE,
            Request.GetRawParameter,
            wIndex=parameter,
            data_or_wLength=math.ceil(get_parameter_size(parameter) / 8),
        )

    def set_raw_parameter(self, parameter: USCParameter, value: int):
        # wIndex is two bytes. The high byte is the value length in bytes, and the low
        # byte is the parameter number
        parameter_size = math.ceil(get_parameter_size(parameter) / 8)
        return self.dev.ctrl_transfer(
            CONTROL_TRANSFER_SET_TYPE,
            Request.SetRawParameter,
            wValue=value,
            wIndex=(parameter_size << 8) + parameter,
        )

    @classmethod
    def get_all(cls) -> typing.Iterable[Maestro]:
        """Returns an iterator over all connected Maestro devices."""
        return map(
            cls.for_device, usb.core.find(find_all=True, custom_match=is_maestro)
        )

    @classmethod
    def get_one(cls) -> Maestro:
        """Get a currently-connected Maestro device.

        If more than one is connected, it is undefined as to which device is returned.

        :raise maestro.exceptions.NoMaestroAvailable: if no Maestro is available.
        """
        dev = usb.core.find(custom_match=lambda dev: is_maestro(dev))
        if dev:
            return cls.for_device(dev)
        else:
            raise NoMaestroAvailable

    @classmethod
    def get_by_serial_number(cls, serial_number):
        """Get a currently-connected Maestro device by its serial number.

        :raise maestro.exceptions.NoMaestroAvailable: if no Maestro is available.
        """
        dev = usb.core.find(
            custom_match=lambda dev: is_maestro(dev)
            and dev.langids
            and dev.serial_number == serial_number
        )
        if dev:
            return cls.for_device(dev)
        else:
            raise NoMaestroAvailable

    def clear_errors(self):
        return self.dev.ctrl_transfer(
            CONTROL_TRANSFER_SET_TYPE,
            Request.ClearErrors,
            wValue=0,
            wIndex=0,
        )

    def reinitialize(self):
        return self.dev.ctrl_transfer(
            CONTROL_TRANSFER_SET_TYPE,
            Request.Reinitialize,
            wValue=0,
            wIndex=0,
        )


class MicroMaestro(Maestro):
    def __init__(self, dev, **kwargs):
        super().__init__(dev, **kwargs)


class MiniMaestro(Maestro):
    def refresh_values(self):
        ret = self.dev.ctrl_transfer(
            CONTROL_TRANSFER_REQUEST_TYPE,
            Request.GetVariablesMiniMaestro,
            data_or_wLength=ServoStatus.size * self.channel_count,
            timeout=self.timeout,
        )
        for i in range(0, len(ret), ServoStatus.size):
            position, target, speed, acceleration = ServoStatus.unpack(
                ret[i : i + ServoStatus.size]
            )
            channel = self[i // ServoStatus.size]

            channel._position = position
            channel._target = target
            channel._speed = speed
            channel._acceleration = acceleration
