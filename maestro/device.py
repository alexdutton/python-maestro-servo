import math
from typing import List, Optional

import usb.core

from maestro.channel import Channel
from maestro.constants import CONTROL_TRANSFER_REQUEST_TYPE, CONTROL_TRANSFER_SET_TYPE
from maestro.structs import ServoStatus
from .enums import Request, USCParameter, ChannelMode, get_parameter_size


def is_maestro(dev):
    return dev.idVendor == 0x1FFB and dev.idProduct in (137, 138, 139, 140)


PRODUCT_CHANNEL_COUNTS = {
    137: 6,
    138: 12,
    139: 18,
    140: 24,
}


class Maestro:
    _group_modes: List[int]

    def __init__(self, dev: usb.core.Device, timeout=5000):
        if type(self) == Maestro:
            raise TypeError("Don't initialize this directly; use Maestro.for_device()")

        self.dev = dev
        self.timeout = timeout

        modes = self._get_modes()

        print(modes)
        self._channels = [
            Channel(self, i, mode=modes[i]) for i in range(self.channel_count)
        ]

    @property
    def channel_count(self):
        return PRODUCT_CHANNEL_COUNTS[self.dev.idProduct]

    @classmethod
    def for_device(cls, dev: usb.core.Device, **kwargs):
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
    def serial_number(self):
        return self.dev.serial_number

    def refresh_variables(self):
        raise NotImplementedError

    def get_raw_parameter(self, parameter: USCParameter):
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
    def get_all(cls):
        return map(
            cls.for_device, usb.core.find(find_all=True, custom_match=is_maestro)
        )

    @classmethod
    def get_one(cls):
        dev = usb.core.find(custom_match=lambda dev: is_maestro(dev))
        if dev:
            return cls.for_device(dev)

    @classmethod
    def get_by_serial_number(cls, serial_number):
        dev = usb.core.find(
            custom_match=lambda dev: is_maestro(dev)
            and dev.langids
            and dev.serial_number == serial_number
        )
        if dev:
            return cls.for_device(dev)

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

            if channel.mode == ChannelMode.Input:
                print(i // ServoStatus.size, target)
