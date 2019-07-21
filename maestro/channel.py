from maestro.enums import ChannelMode


class Channel:
    def __init__(self, maestro, i, mode):
        self.maestro = maestro
        self.i = i
        self._mode = mode
        self._value = None

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        raise NotImplementedError

    @property
    def value(self):
        if self.mode != ChannelMode.Input:
            raise ValueError("This is not an input")
        return self._value
