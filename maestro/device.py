import math

import usb.core

from maestro.channel import Channel
from maestro.constants import CONTROL_TRANSFER_REQUEST_TYPE
from maestro.structs import ServoStatus
from .enums import Request, USCParameter, parameter_sizes, ChannelMode


def is_maestro(dev):
    return dev.idVendor == 0x1FFB and dev.idProduct in (137, 138, 139, 140)


class Maestro:
    def __init__(self, dev: usb.core.Device, servo_count, timeout=5000):
        if type(self) == Maestro:
            raise TypeError("Don't initialize this directly; use Maestro.for_device()")

        self.dev = dev
        self.servo_count = servo_count
        self.timeout = timeout

        modes = self._get_modes()

        self._channels = [Channel(self, i, modes[i]) for i in range(self.servo_count)]

        self.get_settings()

    @classmethod
    def for_device(cls, dev: usb.core.Device, **kwargs):
        if not is_maestro(dev):
            raise ValueError("This isn't a Maestro")
        if dev.idProduct == 137:
            return MicroMaestro(dev, **kwargs)
        elif dev.idProduct == 138:
            return MiniMaestro(dev, servo_count=12, **kwargs)
        elif dev.idProduct == 139:
            return MiniMaestro(dev, servo_count=18, **kwargs)
        elif dev.idProduct == 140:
            return MiniMaestro(dev, servo_count=24, **kwargs)
        else:
            raise ValueError("Unexpected productID: {}".format(dev.idProduct))

    def _get_modes(self):
        modes = []
        for i in range(6):
            group_modes = self.get_raw_parameter(USCParameter.ChannelModes0To3 + i)[0]
            for j in range(4):
                modes.append(ChannelMode(group_modes & 0b11))
                group_modes >>= 2
        return modes

    def __getitem__(self, index):
        return self._channels[index]

    @property
    def serial_number(self):
        return self.dev.serial_number

    def refresh_variables(self):
        raise NotImplementedError

    def get_raw_parameter(self, parameter):
        return self.dev.ctrl_transfer(
            CONTROL_TRANSFER_REQUEST_TYPE,
            Request.GetRawParameter,
            wIndex=parameter,
            data_or_wLength=math.ceil(parameter_sizes[parameter] / 8),
        )

    def get_settings(self):
        for i in range(6):
            self.get_raw_parameter(USCParameter.ChannelModes0To3 + i)

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
            and dev.serial_number == serial_number
        )
        if dev:
            return cls.for_device(dev)


class MicroMaestro(Maestro):
    def __init__(self, dev, **kwargs):
        super().__init__(dev, servo_count=6, **kwargs)


class MiniMaestro(Maestro):
    def refresh_values(self):
        ret = self.dev.ctrl_transfer(
            CONTROL_TRANSFER_REQUEST_TYPE,
            Request.GetVariablesMiniMaestro,
            data_or_wLength=ServoStatus.size * self.servo_count,
            timeout=self.timeout,
        )
        for i in range(0, len(ret), ServoStatus.size):
            position, target, speed, acceleration = ServoStatus.unpack(
                ret[i : i + ServoStatus.size]
            )
            channel = self[i // ServoStatus.size]
            if channel.mode == ChannelMode.Input:
                channel._value = target / (2 ** 10)
