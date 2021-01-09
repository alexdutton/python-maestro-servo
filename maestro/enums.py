import enum
import typing


class ChannelMode(enum.IntEnum):
    """Channel mode."""

    Servo = 0
    """The channel is a servo."""
    ServoMultiplied = 1  # unused, as far as I can tell
    """This value is defined within the Maestro Control Centre, but unused.
    
    It is not recommended to use this channel mode, as its purpose is unclear."""
    Output = 2
    """The channel is an output.
    
    Output channels are controlled with a value in the range [0, 1023], which maps onto
    the range [0, Vcc] volts."""
    Input = 3
    """The channel is an input.
    
    The value is in the range [0, 1), corresponding to the input voltage range [0, Vcc]
    volts."""


class USCParameter(enum.IntEnum):
    """Constants for getting and setting Maestro parameters."""

    Initialized = 0
    ServosAvailable = 1
    ServoPeriod = 2
    SerialMode = 3
    SerialTimeout = 6
    ChannelModes0To3 = 12
    ChannelModes4To7 = 13
    ChannelModes8To11 = 14
    ChannelModes12To15 = 15
    ChannelModes16To19 = 16
    ChannelModes20To23 = 17

    ServoMultiplier = 26

    # Servo 0 is at base, servo 1 is 9 up, servo 2 is 18 up, and so on.
    ServoHomeBase = 30
    ServoMinBase = 32
    ServoMaxBase = 33
    ServoNeutralBase = 34
    ServoRangeBase = 36
    ServoSpeedBase = 37
    ServoAccelerationBase = 38


_parameter_sizes: typing.Dict[USCParameter, int] = {
    USCParameter.Initialized: 8,
    USCParameter.ServosAvailable: 8,
    USCParameter.ServoPeriod: 8,
    USCParameter.SerialMode: 2,
    USCParameter.SerialTimeout: 16,
    USCParameter.ChannelModes0To3: 8,
    USCParameter.ChannelModes4To7: 8,
    USCParameter.ChannelModes8To11: 8,
    USCParameter.ChannelModes12To15: 8,
    USCParameter.ChannelModes16To19: 8,
    USCParameter.ChannelModes20To23: 8,
    USCParameter.ServoMultiplier: 8,
    USCParameter.ServoHomeBase: 15,
    USCParameter.ServoMinBase: 8,
    USCParameter.ServoMaxBase: 8,
    USCParameter.ServoNeutralBase: 15,
    USCParameter.ServoRangeBase: 6,
    USCParameter.ServoSpeedBase: 8,
    USCParameter.ServoAccelerationBase: 8,
}
"""Parameter sizes in bits

To find the number of bytes for the response, take math.ceil(size / 8.0).
"""


def get_parameter_size(parameter: USCParameter) -> int:
    if parameter >= USCParameter.ServoHomeBase:
        parameter = (
            (parameter - USCParameter.ServoHomeBase) % 9
        ) + USCParameter.ServoHomeBase

    if parameter in _parameter_sizes:
        return _parameter_sizes[parameter]
    else:
        raise KeyError(parameter)


class Request(enum.IntEnum):
    """Constants for Maestro USB control requests.

    See :doc:`protocol` for more details about control requests."""

    GetRawParameter = 129  # REQUEST_GET_PARAMETER
    SetRawParameter = 130  # REQUEST_SET_PARAMETER
    GetVariablesMicroMaestro = 131  # REQUEST_GET_VARIABLES
    SetServoVariable = 132  # REQUEST_SET_SERVO_VARIABLE
    SetTarget = 133  # REQUEST_SET_TARGET
    ClearErrors = 134  # REQUEST_CLEAR_ERRORS
    GetVariablesMiniMaestro = 135  # REQUEST_GET_SERVO_SETTINGS
    GetStack = 136  # REQUEST_GET_STACK
    GetCallStack = 137  # REQUEST_GET_CALL_STACK
    SetPWM = 138  # REQUEST_SET_PWM
    Reinitialize = 144  # REQUEST_REINITIALIZE
    EraseScript = 160  # REQUEST_ERASE_SCRIPT
    WriteScript = 161  # REQUEST_WRITE_SCRIPT
    SetScriptDone = 162  # REQUEST_SET_SCRIPT_DONE
    RestartScriptAtSubroutine = 163  # REQUEST_RESTART_SCRIPT_AT_SUBROUTINE
    RestartScriptAtSubroutineWithParameter = (
        164  # REQUEST_RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER
    )
    RestartScript = 165  # REQUEST_RESTART_SCRIPT
    StartBootloader = 255  # REQUEST_START_BOOTLOADER


class ServoVariableMask(enum.IntEnum):
    Speed = 0
    Acceleration = 128
