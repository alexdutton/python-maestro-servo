import enum


class ChannelMode(enum.IntEnum):
    Servo = 0
    ServoMultiplied = 1
    Output = 2
    Input = 3


class USCParameter(enum.IntEnum):
    Initialized = 0
    ServosAvailable = 1
    ServoPeriod = 2
    SerialMode = 3
    ChannelModes0To3 = 12
    ChannelModes4To7 = 13
    ChannelModes8To11 = 14
    ChannelModes12To15 = 15
    ChannelModes16To19 = 16
    ChannelModes20To23 = 17


parameter_sizes = {
    USCParameter.ChannelModes0To3: 8,
    USCParameter.ChannelModes4To7: 8,
    USCParameter.ChannelModes8To11: 8,
    USCParameter.ChannelModes12To15: 8,
    USCParameter.ChannelModes16To19: 8,
    USCParameter.ChannelModes20To23: 8,
}


class Request(enum.IntEnum):
    GetRawParameter = 129
    GetVariablesMiniMaestro = 135
    GetVariablesMicroMaestro = 131
